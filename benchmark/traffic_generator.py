import socket
import time
import random

class TrafficGenerator:
    """
    Traffic generator - can generate traffice via tcp or udp with uniform or burst distribution
    """
    def __init__(self, addr, port, timeout, protocol, pkt_size, bandwidth, distribution, duration):
        self.addr = addr
        self.port = port
        self.timeout = timeout

        self.protocol = protocol
        self.pkt_size = pkt_size
        self.bandwidth = bandwidth
        self.distribution = distribution
        self.duration = duration

        self.seq_num = 0
        self.SEQ_C = 30

        self.config_protocol()

    def config_protocol(self):
        """
        configure sockets according to selected protocol
        """
        if self.protocol == "tcp":
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.addr, self.port))

            self.send_func = self.send_tcp_pkt
            self.recv_func = self.recv_tcp_pkt

        elif self.protocol == "udp":
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            self.send_func = self.send_udp_pkt
            self.recv_func = self.recv_udp_pkt

        else:
            raise ValueError("Incorrect protocol - usage: 'tcp' or 'udp'")

        self.sock.settimeout(self.timeout)
    
    def send_tcp_pkt(self, send_pkt):
        self.sock.send(send_pkt)

    def recv_tcp_pkt(self):
        try:
            data = self.sock.recv(self.pkt_size + self.SEQ_C)
        except socket.timeout:
            return None
        return data

    def send_udp_pkt(self, send_pkt):
        self.sock.sendto(send_pkt, (self.addr, self.port))

    def recv_udp_pkt(self):
        try:
            data, _ = self.sock.recvfrom(self.pkt_size + self.SEQ_C)
        except socket.timeout:
            return None
        return data

    def gen_pkt(self):
        pkt = bytes([random.randint(0, 255) for _ in range(self.pkt_size)])
        seq_b = "@@@@@@@@@@@@@@" + str(self.seq_num)
        pkt += seq_b.encode()
        return pkt

    def run_traffic_uniform(self):
        ooo_count = 0
        send_pkt_count = 0
        recv_pkt_count = 0
        rtt = list()
        
        start_time = time.monotonic()
        interval = float(1.0 / self.bandwidth)

        while time.monotonic() - start_time < self.duration:
            send_pkt = self.gen_pkt()
            send_time = time.monotonic()
            
            self.send_func(send_pkt)
            send_pkt_count += 1

            recv_pkt = self.recv_func()
            recv_time = time.monotonic()

            if recv_pkt:
                self.seq_num += 1
                rtt.append(recv_time - send_time)
                recv_pkt_count += 1

                try:
                    _, recv_seq_num = recv_pkt.split(b"@@@@@@@@@@@@@@", 1)
                    recv_seq_num = int(recv_seq_num.decode().strip('\\'))
                except:
                    recv_seq_num = -1
                if (self.seq_num - 1) != recv_seq_num:
                    ooo_count += 1

            elapsed_time = time.monotonic() - send_time
            delay = interval - elapsed_time
            if delay > 0:
                time.sleep(delay)
        
        return ooo_count, send_pkt_count, recv_pkt_count, rtt

    def run_traffic_burst(self):
        ooo_count = 0
        send_pkt_count = 0
        recv_pkt_count = 0
        rtt_arr = list()
        
        start_time = time.monotonic()
        burst_time = time.monotonic()
        interval = 1
        idx = 0

        while (time.monotonic() - start_time) < self.duration:
            send_pkt = self.gen_pkt()
            send_time = time.monotonic()
            
            self.send_func(send_pkt)
            send_pkt_count += 1

            recv_pkt = self.recv_func()
            recv_time = time.monotonic()
            if recv_pkt:
                self.seq_num += 1

                rtt_arr.append(recv_time - send_time)
                recv_pkt_count += 1

                try:
                    _, recv_seq_num = recv_pkt.split(b"@@@@@@@@@@@@@@", 1)
                    recv_seq_num = int(recv_seq_num.decode().strip('\\'))
                except:
                    recv_seq_num = -1
                if (self.seq_num - 1) != recv_seq_num:
                    ooo_count += 1

            if idx >= self.bandwidth:
                elapsed_time = time.monotonic() - burst_time
                burst_time = time.monotonic()
                idx = 0
                delay = interval - elapsed_time
                if delay > 0:
                    time.sleep(delay)
        
        return ooo_count, send_pkt_count, recv_pkt_count, rtt_arr
        

