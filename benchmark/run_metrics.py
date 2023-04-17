import argparse
from statistics import median, mean
from traffic_generator import TrafficGenerator

def calculate_metrics(ooo_count, send_pkt_count, recv_pkt_count, rtt_arr):
    loss_rate = ((send_pkt_count - recv_pkt_count) / send_pkt_count) * 100.0
    ooo_rate = (ooo_count / send_pkt_count) * 100.0
    min_rtt = min(rtt_arr)
    max_rtt = max(rtt_arr)
    median_rtt = median(rtt_arr)
    mean_rtt = mean(rtt_arr)

    return loss_rate, ooo_rate, min_rtt, max_rtt, median_rtt, mean_rtt

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate and send TCP or UDP traffic with specified properties')
    parser.add_argument('-a', '--address', default='localhost', help='Address to use to establish conenction (default: localhost)')
    parser.add_argument('-po', '--port', type=int, default=8000, help='Port to use to establish connection (default: 8000)')
    parser.add_argument('-p', '--protocol', choices=['tcp', 'udp'], default='tcp', help='Transport protocol to use (default: tcp)')
    parser.add_argument('-s', '--packet-size', type=int, default=1024, help='Size of each packet in bytes (default: 1024)')
    parser.add_argument('-b', '--bandwidth', type=float, default=100.0, help='Target bandwidth in packets per second (default: 100)')
    parser.add_argument('-d', '--distribution', choices=['uniform', 'burst'], default='uniform', help='Packet sending distribution (default: uniform)')
    parser.add_argument('-t', '--duration', type=int, default=10, help='Duration of the transmission in seconds (default: 10)')

    args = parser.parse_args()

    tg = TrafficGenerator(args.address, args.port, 5, args.protocol, args.packet_size, args.bandwidth, args.distribution, args.duration)

    if args.distribution == 'uniform':
        ooo_count, send_pkt_count, recv_pkt_count, rtt_arr = tg.run_traffic_uniform()
    elif args.distribution == 'burst':
        ooo_count, send_pkt_count, recv_pkt_count, rtt_arr = tg.run_traffic_burst()
    else:
        ValueError("Incorrect distribution - usage 'uniform' or 'burst'")
    loss_rate, ooo_rate, min_rtt, max_rtt, median_rtt, mean_rtt = calculate_metrics(ooo_count, send_pkt_count, recv_pkt_count, rtt_arr)
    
    print("================================================================================================================================")
    print(f"Benchmarking {args.protocol.upper()} with {args.distribution} traffic distribution, {args.bandwidth} pkts/sec bandwidth, {args.packet_size} packet size for {args.duration} seconds")
    print("================================================================================================================================")
    print("Results:")
    print(f"Loss rate: {loss_rate:.2f}%")
    print(f"Out of order packet rate: {ooo_rate:.2f}%")
    print(f"RTT - min: {min_rtt:.5f}, max: {max_rtt:.5f}, mean: {mean_rtt:.5f}, median: {median_rtt:.5f}")