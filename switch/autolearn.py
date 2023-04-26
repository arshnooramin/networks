import struct
import math
import sys

# store switch table as a global hashmap with mac as index and link_id as value
switch_hm = dict()

# store rx and tx metric in global hashmap with link_id as index and count as value
rx_metric, tx_metric = dict(), dict()

rx_count, tx_count = 0, 0

def init_links(filename):
    global rx_metric, tx_metric

    with open(filename, 'rb') as f:
        raw = f.read(14)
        while raw:
            _, link_id = struct.unpack("BB", raw[0:2])

            rx_metric[link_id] = 0
            tx_metric[link_id] = 0
            
            raw = f.read(14)

def handle_frame(srcmac, destmac, link_id):
    global switch_hm, rx_metric, tx_metric

    # record incoming link and MAC (link layer) source address
    switch_hm[srcmac] = link_id

    # increment rx for link_id
    rx_metric[link_id] += 1

    # index switch table using MAC (link layer) destination address
    # if entry found for destination
    if destmac in switch_hm:
        # if entry found for destination
        if switch_hm[destmac] == link_id:
            # drop the frame
            return "DROP"
        else:
            out_link_id = switch_hm[destmac]
            # increment tx for link_id, if it doesn't exist initialize entry
            tx_metric[out_link_id] += 1
            # forward frame on interface indicated by entry
            return out_link_id
    else:    
        # increment tx for all existing link ids except current
        for c_link_id in tx_metric:
            if c_link_id != link_id:
                tx_metric[c_link_id] += 1
        # flood
        return 0xff

def print_stats():
    global rx_count, tx_count

    print("{:>5} | {:>13} | {:>13}".format(
          "Link",
          "RX",
          "TX"))
    print("------|---------------|---------------")

    for link_id in rx_metric:
        rm_str = f"{rx_metric[link_id]} ({rx_metric[link_id]/rx_count*100:.1f}%)"
        tm_str = f"{tx_metric[link_id]} ({tx_metric[link_id]/tx_count*100:.1f}%)"
        print("{:5x} | {:>13} | {:>13}".format(
            link_id,
            rm_str,
            tm_str          
        ))

def print_trace(filename):
    # compute the table width
    wd = 2*12+10+9
    wd -= len(filename)
    wd -= 2 # spaces

    # print the table name
    print(math.floor(wd/2)*"*",
            filename,
            "*"*math.ceil(wd/2))

    # print the table header
    print("{:>5} | {:>5} | {:>12} | {:>12} | {:>6}".format(
          "SWID",
          "LnkID",
          "  DESTMAC   ",
          "   SRCMAC   ",
          "OutLnk"))
    print("------|-------|--------------|--------------|--------")

    with open(filename, 'rb') as f:
        raw = f.read(14)
        while raw:
            sw_id, link_id = struct.unpack("BB", raw[0:2])
            #destmac = raw[2:8]

            # struct.unpack doesn't handle 6-byte integers, so we need to
            # pad the first two bytes with 0 to make it 8 bytes 
            destmac = struct.unpack("!Q",  b"\x00\x00" + raw[2:8])[0]
            srcmac = struct.unpack("!Q",  b"\x00\x00" + raw[8:14])[0]

            outlnk = handle_frame(srcmac, destmac, link_id)
            if type(outlnk) == int: outlnk = str(hex(outlnk))[2:]
                        
            print("{:5x} | {:5x} | {:012x} | {:012x} | {:>6}".format(
                sw_id,
                link_id,
                destmac,
                srcmac,
                outlnk                
            ))
            
            # read next packet
            raw = f.read(14)

if __name__=="__main__":
    if len(sys.argv) == 1:
        print("Usage: ptrace [trace file.out]")
    
    # probably should use argparse here...
    for f in sys.argv[1:]:
        if f.endswith(".out"):
            init_links(f)
            print_trace(f)
            print("\nSummary:")

            rx_count = sum(rx_metric.values())
            tx_count = sum(tx_metric.values())
            print_stats()