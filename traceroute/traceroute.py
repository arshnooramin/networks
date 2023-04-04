import socket
import sys
import random
import struct
import time
from classping import icmp_socket, checksum

def traceroute(hostname, port, max_hops=30, sttl=1):
    # get the destination address
    dest_addr = socket.gethostbyname(hostname)

    for ttl in range(sttl, max_hops + 1):
        # configure icmp socket
        icmp_sock = icmp_socket()

        ident = random.randint(0, 0xffff)
        header = struct.pack("!BBHHH", 8, 0, 0, ident, 1)
        send_time_ns = int (1e9 * time.time())
        payload = struct.pack ("!Q", send_time_ns)

        packet = header + payload
        
        c = checksum(packet)
        header = struct.pack("!BBHHH", 8, 0, c, ident, 1)
        packet = header + payload

        # configure udp socket
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udp_sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

        # send the ping
        udp_sock.sendto(packet, (dest_addr, port))

        addr = None
        try:
            # if message received
            resp, addr = icmp_sock.recvfrom(1024)
            # get the address of the source
            addr = addr[0]
            # try to get hostname
            try:
                name = socket.gethostbyaddr(addr)[0]
            except:
                name = addr
            print(f"{ttl} {name} ({addr})")
        except:
            print(f"{ttl} * (*)")
        finally:
            # close sockets
            icmp_sock.close()
            udp_sock.close()
        
        # if the destination is reached break
        if addr and addr == dest_addr:
            print(f"Reached host {hostname} in {ttl} hops")
            break

if __name__ == "__main__":
    # expect a cli argument for the destination hostname
    try:
        hostname = sys.argv[1]
    except:
        raise ValueError("Usage: python traceroute.py [hostname]")
    port = 33434
    traceroute(hostname=hostname, port=port)