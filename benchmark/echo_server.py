"""
echo server - generated using Chat GPT
prompt: generate a echo server that can accept tcp or udp packets on a specified port and echo them back to the sender as quickly as possible. 
"""
import socket
import argparse

SEQ_C = 30

def tcp_echo_server(host, port, buf_size):
    """
    tcp echo server
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        conn, addr = s.accept()
        with conn:
            while True:
                data = conn.recv(buf_size)
                if not data:
                    break
                conn.sendall(data)

def udp_echo_server(host, port, buf_size):
    """
    udp echo server
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', port))
        while True:
            data, addr = s.recvfrom(buf_size)
            s.sendto(data, addr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a TCP or UDP echo server')
    parser.add_argument('-p', '--protocol', choices=['tcp', 'udp'], default='tcp', help='Transport protocol to use (default: tcp)')
    parser.add_argument('-a', '--address', default='0.0.0.0', help='Address to use to establish conenction (default: 0.0.0.0)')
    parser.add_argument('-po', '--port', type=int, default=8000, help='Port to use to establish connection (default: 8000)')
    parser.add_argument('-bs', '--bufsize', type=int, default=1024, help='Buffer size (default: 1024)')

    args = parser.parse_args()

    print(f"Starting {args.protocol.upper()} echo server on {args.address}:{args.port}")

    if args.protocol == 'tcp':
        tcp_echo_server(args.address, args.port, args.bufsize + SEQ_C)
    elif args.protocol == 'udp':
        udp_echo_server(args.address, args.port, args.bufsize + SEQ_C)
    else:
        ValueError("Incorrect protocol - usage 'tcp' or 'udp'")