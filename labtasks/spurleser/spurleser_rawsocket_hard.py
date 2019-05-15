#!/usr/bin/env python3

"""
Quelle: https://github.com/gere/tracepy/blob/master/tracepy.py

Eigene Implementierung von traceroute unter Verwendung von Raw Sockets und selbst-implementierter Zuordnung von Antwort-zu-Anfrage-Paketen.

```bash
$ sudo ./spurleser_rawsocket_hard.py 8.8.8.8
DEBUG:__main__:Sent from port=63076 ttl=1 to 8.8.8.8:33435
DEBUG:__main__:Received 64 bytes from 192.168.27.1
 1    192.168.27.1
...
Reached destination 8.8.8.8 at ttl=10
```
"""

import socket
import sys
import os
import argparse
import logging
import binascii
from struct import *
from time import sleep
from collections import namedtuple

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

"""
    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |Version|  IHL  |Type of Service|          Total Length         |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |         Identification        |Flags|      Fragment Offset    |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |  Time to Live |    Protocol   |         Header Checksum       |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                       Source Address                          |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Destination Address                        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Options                    |    Padding    |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
"""
ipv4_header = namedtuple('ipv4_header',
                         'version_ihl tos length ident flags ttl proto checksum source destination')
ipv4_header_format  = '!BBHHHBBH4s4s'


"""
        0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |     Type      |     Code      |          Checksum             |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |               rest of the message / unused                    |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |      Internet Header + 64 bits of Original Data Datagram      |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
"""
icmp_header = namedtuple('icmp_header', 'type code checksum rest')
icmp_header_format = '!BBHI'    


"""
 0      7 8     15 16    23 24    31  
 +--------+--------+--------+--------+ 
 |     Source      |   Destination   | 
 |      Port       |      Port       | 
 +--------+--------+--------+--------+ 
 |                 |                 | 
 |     Length      |    Checksum     | 
 +--------+--------+--------+--------+ 
 """
udp_header = namedtuple('udp_header', 'source_port dest_port length checksum')
udp_header_format = '!HHHH'



"""
struct format for packet headers 
Python formats
Format      C Type          Python type             Standard size   
x           pad byte        no value         
c           char            bytes of length 1       1
b           signed char     integer                 1
B           unsigned char   integer                 1
?           _Bool           bool                    1
h           short           integer                 2
H           unsigned short  integer                 2
i           int             integer                 4
I           unsigned int    integer                 4
l           long            integer                 4
L           unsigned long   integer                 4
q           long long       integer                 8
Q           unsigned long long  integer             8
n           ssize_t         integer     
N           size_t          integer         
e           (7)             float                   2
f           float           float                   4
d           double          float                   8
s           char[]          bytes        
p           char[]          bytes        
P           void *          integer         
"""

# Command line arguments
parser = argparse.ArgumentParser(description='A traceroute alternative')
parser.add_argument('host', type=str, nargs=1,
                    help='The host for which the path is to be examined')


def makeHeader(hdrType, hdrFormat, buf):
    """
    Given a named tuple type, a struct format and a buffer, 
    this function creates and returns an instance of the named tuple
    with contents filled from the buffer.
    """
    return hdrType._make(unpack_from(hdrFormat, buf))


def dissect_icmp_packet(buffer):
    ip4_h = makeHeader(ipv4_header, ipv4_header_format, buffer)       
    version = (ip4_h.version_ihl & 0xF0) >> 4
    ihl = (ip4_h.version_ihl & 0x0F)
    #TODO: better handling of error
    if (version != 4 or ihl != 5 or ip4_h.proto != 1):
        print("can't handle this ip4 packet")
        return  

    ip4_h_size = calcsize(ipv4_header_format) # always 20 bytes since packet with ihl > 5 are discarded
    icmp_hdr = makeHeader(icmp_header, icmp_header_format, buffer[ip4_h_size:])
    
    """
    Type 0 — Echo Reply
    Type 1 — Unassigned
    Type 2 — Unassigned
    Type 3 — Destination Unreachable
    Type 4 — Source Quench (Deprecated)
    Type 5 — Redirect
    Type 6 — Alternate Host Address (Deprecated)
    Type 7 — Unassigned
    Type 8 — Echo
    Type 9 — Router Advertisement
    Type 10 — Router Selection
    Type 11 — Time Exceeded         **********
    ...
    """
    if (icmp_hdr.type != 11 or icmp_hdr.code != 0):
        print("can't handle this icmp packet")
        return
    
    icmp_h_size = calcsize(icmp_header_format) # 8 bytes. That's a constants        
    icmp_data = buffer[(ip4_h_size + icmp_h_size):]

    return (icmp_hdr, icmp_data)


def send_probe(send_socket, address, packet, ttl):
    send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)   
    b = send_socket.sendto(packet, address)
    port_number = send_socket.getsockname()[1]      
    return port_number


def start(host):        
    MAX_TTL = 64
    # Ziel aufloesen (wichtig falls eine Domain statt einer IP-Adresse uebergeben wurde)
    dst_ip = socket.gethostbyname(host)
    # Dies ist der Zielport, der beim Ziel per UDP angesprochen wird.
    # Waehrend des Laufens, wird er inkrementiert.
    dst_port = 33435
    #dst_port = 35353       # this does not work, some routers seem to block this port range
    # Startwert fuer die IPv4 Time-to-live
    ttl = 1
    # Zaehler fuer Timeouts
    timeoutCount = 0

    # Konstruiere Payload fuer das UDP-Probepaket. Hier 4x die eigene Prozess-ID.
    pid = os.getpid()
    probe_payload = pack('!HHHH', pid, pid, pid, pid)

    # Erzeuge einen UDP-Socket zum Senden der Probes
    # Informationen zur Socket-Erstellung: https://docs.python.org/3/library/socket.html#socket.socket
    try:
        send_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
    except socket.error: 
        logger.fatal('Erzeugen des Sendesockets fehlgeschlagen.', exc_info=True)
        sys.exit()
    try:
        listen_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_RAW, proto=socket.IPPROTO_ICMP)
    except socket.error: 
        logger.fatal('Erzeugen des Empfangssockets fehlgeschlagen.', exc_info=True)
        sys.exit()
    listen_socket.setsockopt(socket.SOL_IP, socket.IP_HDRINCL, 1)
    listen_socket.settimeout(3)
    
    # Abbrechen wenn die TTL zu gross ist
    while ttl < MAX_TTL:
        # Sende maximal n Probes pro TTL-Wert
        if timeoutCount >= 3:
            ttl += 1
            timeoutCount = 0
            dst_port += 1
        
        # Sende eine Probe
        port_number = send_probe(send_socket, (dst_ip, dst_port), probe_payload, ttl)
        logger.debug(f'Sent from port={port_number} ttl={ttl} to {dst_ip}:{dst_port}')

        # Empfange ein ICMP-Paket
        try:
            # data ist das empfangene Paket inklusive IPv4-Header.
            # addr enthaelt Informationen ueber den Absender des Pakets.
            data, addr = listen_socket.recvfrom(1508)
            logger.debug(f'Received {len(data)} bytes from {addr[0]}')
        except socket.timeout:
            logger.debug(f"timeout {timeoutCount} at hop ttl={ttl}")
            timeoutCount += 1
            continue
        
        # Falls eine Antwort vom Zielsystem kam, dann haben wir das Ziel erreicht
        # und sind fertig.
        if addr[0] == dst_ip:
            print(f'Reached destination {dst_ip} at ttl={ttl}')
            break

        # Andernfalls kam das ICMP-Paket vermutlich von einem Router auf der Strecke.
        # Parse das ICMP-Paket
        icmp_hdr, icmp_data = dissect_icmp_packet(data)
        # Das ICMP-Paket schickt einen Teil der Originaldaten zurueck.
        # Stelle aus den zurueckgeschickten Daten wieder ein UDP/IP-Paket her, sodass
        # spaeter abgeglichen werden kann, ob dies einem unserer Probes entspricht.
        original_ip4_hdr = makeHeader(ipv4_header, ipv4_header_format, icmp_data)
        original_udp_hdr = makeHeader(udp_header, udp_header_format, icmp_data[calcsize(ipv4_header_format):])
        original_payload = icmp_data[calcsize(ipv4_header_format)+calcsize(udp_header_format):]
        #print(binascii.hexlify(original_payload))

        if original_udp_hdr.source_port == port_number:
            print(f"%2d    %s" % (ttl, addr[0]))
            ttl += 1
            timeoutCount = 0
            dst_port += 1
    if ttl > MAX_TTL:
        logger.debug(f"Abbruch da TTL > {MAX_TTL}")



if __name__ == '__main__':
    args = parser.parse_args()
    try:
        start(args.host[0])
    except KeyboardInterrupt:
        print()
        sys.exit(0)
