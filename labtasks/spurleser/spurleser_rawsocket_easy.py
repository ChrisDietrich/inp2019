#!/usr/bin/env python2

"""
A minimal traceroute implementation using raw socket.

This is probably not the best example from a didactic perspective because it avoids the problem to match received ICMP replies to previously sent UDP requests. Instead it binds the ICMP raw socket to a "port" which signals the kernel to perform the matching for us. To highlight what would be needed, it might make sense to just have a raw socket that is NOT bound to a "port" and require the programmer to match herself.

Originally based on http://blog.ksplice.com/2010/07/learning-by-doing-writing-your-own-traceroute-in-8-easy-steps/.

$ sudo ./minimal_traceroute_rawsocket.py
    1 fritz.box (192.168.27.1)
    2 dslb-084-059-211-001.084.059.pools.vodafone-ip.de (84.59.211.1)
    3 88.79.20.14 (88.79.20.14)
    4 88.79.20.28 (88.79.20.28)
    5 188.111.129.20 (188.111.129.20)
    6 145.254.2.189 (145.254.2.189)
    7 72.14.222.128 (72.14.222.128)
    8 108.170.241.172 (108.170.241.172)
    9 209.85.255.214 (209.85.255.214)
   10 108.170.234.11 (108.170.234.11)
   11 209.85.252.28 (209.85.252.28)
   12 108.170.252.1 (108.170.252.1)
   13 66.249.94.147 (66.249.94.147)
   14 fra15s12-in-f14.1e100.net (216.58.208.46)
Reached the destination host 216.58.208.46
"""

import socket

def traceroute(dest_name):
    """
    Performs a minimal traceroute to a given destination host/IP address.
    
    Sends a UDP packet to the destination in a loop with increasing IP TTL values.
    """
    # Resolve the destination hostname to an IP address
    dest_addr = socket.gethostbyname(dest_name)
    port = 33434
    max_hops = 30
    icmp = socket.getprotobyname('icmp')
    udp = socket.getprotobyname('udp')
    ttl = 1
    while ttl <= max_hops:
        # Create a raw socket for ICMP messages because we expect ICMP Time-to-live exceeded 
        # messages in response to our requests unless the destination is reached.
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        # Create a UDP socket which we use to send the UDP requests
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

        # Make the ICMP recv socket only bind to our port. 
        # NOTE: This is not intuitive because ICMP does not have the concept of ports.
        #       However, it works and it lifts the work to match ICMP replies to requests that 
        #       were previously sent. The kernel seems to do this for us.
        recv_socket.bind(("", port))
        send_socket.sendto("", (dest_name, port))
        curr_addr = None
        curr_name = None
        try:
            # recvfrom returns a pair (string, address) where string is a string representing the 
            # data received and address is the address of the socket sending the data
            _, curr_addr = recv_socket.recvfrom(512)
            curr_addr = curr_addr[0]
            try:
                # Try to resolve the remote IP address which sent the ICMP pkt to a hostname
                curr_name = socket.gethostbyaddr(curr_addr)[0]
            except socket.error:
                curr_name = curr_addr
        except socket.error:
            pass
        finally:
            send_socket.close()
            recv_socket.close()

        # Print a line with the IP address and the resolved hostname (if available)
        if curr_addr is not None:
            curr_host = "%s (%s)" % (curr_name, curr_addr)
        else:
            curr_host = "*"
        print "%5d %s" % (ttl, curr_host)

        ttl += 1
        if curr_addr == dest_addr:
            print "Reached the destination host %s" % (dest_addr,)
            break

if __name__ == "__main__":
    traceroute('google.com')

