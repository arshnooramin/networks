import socket
import struct
import time

class Traceroute:
    def __init__(self, dest, hops):
        self.dest = dest
        self.hops = hops
        self.ttl = 1
        self.port = 33434
    
    def run_trace():
        
    
    def get_receiver(self):
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP
        )

        try:
            sock.bind(('', self.port))
        except:
            raise ConnectionError("Failed to bind receiver socket")

        return sock
    
    def get_sender(self):
        sock = socket.socket(
            socket.AF_INET, socket.sock_DGRAM, socket.IPPROTO_UDP
        )

        sock.setsockopt(socket.SOL_IP, socket.IP_TTL, self.ttl)

        return sock

def traceroute(host):
    """Perform a traceroute to the given host."""
    port = 33434
    max_hops = 30
    icmp = socket.getprotobyname("icmp")
    udp = socket.getprotobyname("udp")
    ttl = 1
    while True:
        # Create sockets for sending and receiving UDP packets.
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
        receiver = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        receiver.settimeout(3.0)
        receiver.bind(("", port))
        
        # Set the time-to-live (TTL) for the outgoing packet.
        sender.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        
        # Send a UDP packet to the target host with the current TTL.
        sender.sendto(b"", (host, port))
        
        # Record the time the packet was sent.
        start_time = time.time()
        
        # Wait for a response from the target host or a timeout.
        try:
            _, addr = receiver.recvfrom(512)
            end_time = time.time()
            _, _, _, _, ttl, _ = struct.unpack("!BBHHHBBH4s4s", _) # Unpack the received packet
            addr = addr[0]
        except socket.timeout:
            addr = None
            end_time = None
        
        # Print the results for this hop.
        if addr:
            print(f"{ttl} {addr} {end_time - start_time:.3f} ms")
        else:
            print(f"{ttl} *")
        
        # Close the sockets.
        sender.close()
        receiver.close()
        
        # Exit if we've reached the maximum number of hops or the target host.
        ttl += 1
        if addr == host or ttl > max_hops:
            break

traceroute("bbc.co.uk")