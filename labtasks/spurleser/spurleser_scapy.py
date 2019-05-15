#!/usr/bin/env python3

"""
Eine traceroute-Implementierung unter Verwendung von scapy.

$ sudo ./spurleser_scapy.py
    1 192.168.27.1
    2 84.59.211.1
    3 88.79.20.10
    4 188.111.173.152
    5 188.111.129.24
    6 145.254.2.205
    7 72.14.222.128
    8 108.170.241.140
    9 216.239.42.213
   10 209.85.244.159
   11 108.170.236.248
   12 108.170.252.1
   13 72.14.232.35
Done! 172.217.22.78
"""

from scapy.all import *

def traceroute_scapy(hostname="google.com"):
    # Erlaube maximal 48 Hops
    for i in range(1, 48):
        # Erzeuge ein UDP-Paket mit Quellport 33434
        udpPkt = UDP(dport=33434)
        # Erzeuge das zu sendende Paket. Die unterste Schicht ist IP, die Schichten darunter 
        # erzeugt scapy automatisch.
        pkt = IP(dst=hostname, ttl=i) / udpPkt

        # Sende das Paket und warte auf eine Antwort (maximal 5 Sekunden)
        reply = sr1(pkt, timeout=5, verbose=0)
        if reply is None:
            # In der vorgegebenen Zeit kam keine Antwort
            break
        elif reply.type == 3:
            # Das Ziel wurde erreicht, denn wir bekamen eine ICMP Port-unreachable-Antwort zurueck
            """
            ###[ ICMP ]###
              type      = dest-unreach
              code      = port-unreachable
              chksum    = 0xc878
              reserved  = 0
              length    = 0
              nexthopmtu= 0
            """
            print(f"Fertig. Das Ziel {reply.src} wurde erreicht.")
            print(reply.show2())
            break
        else:
            # We're in the middle somewhere
            print("%5d %s" % (i, reply.src))

if __name__ == "__main__":
    traceroute_scapy('google.com')
