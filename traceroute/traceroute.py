import socket
import sys

def traceroute(hostname, port, max_hops=30, sttl=1):
    # get the destination address
    dest_addr = socket.gethostbyname(hostname)

    for ttl in range(sttl, max_hops + 1):
        # configure icmp socket
        icmp_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        icmp_sock.settimeout(1)
        icmp_sock.bind(("", port))

        # configure udp socket
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udp_sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

        # send the ping
        udp_sock.sendto("".encode(), (dest_addr, port))

        recv_addr = None
        try:
            # if message received
            _, recv_addr_arr = icmp_sock.recvfrom(512)
            # get the address of the source
            recv_addr = recv_addr_arr[0]
            # try to get hostname
            try:
                recv_name = socket.gethostbyaddr(recv_addr)[0]
            except:
                recv_name = recv_addr
            print(f"{ttl} {recv_name} ({recv_addr})")
        except:
            print(f"{ttl} * (*)")
        finally:
            # close sockets
            icmp_sock.close()
            udp_sock.close()
        
        # if the destination is reached break
        if recv_addr and recv_addr == dest_addr:
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