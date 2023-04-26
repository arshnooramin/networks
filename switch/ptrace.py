"""Simple network trace printer

Format:
Switch ID (1 byte)
Link ID (1 byte)
Destination MAC (6 bytes)
Source MAC (6 bytes)

Alan Marchiori 2019
4/2023 - updated to parse mac addresses into ints
"""
import struct
import math
import sys
"""
SAMPLE OUTPUT
***************** simple_trace.out ******************
 SWID | LnkID |      DESTMAC      |       SRCMAC     
------|-------|-------------------|------------------
    1 |     0 | 77-fe-a6-18-9b-5c | 0f-34-a2-c1-f4-59
    1 |     0 | d6-31-43-eb-d5-05 | 0f-34-a2-c1-f4-59
    1 |     2 | d6-31-43-eb-d5-05 | d6-a7-fe-09-b7-0f
    1 |     3 | d6-a7-fe-09-b7-0f | d6-31-43-eb-d5-05
    1 |     0 | d6-31-43-eb-d5-05 | 0f-34-a2-c1-f4-59
    1 |     0 | d6-a7-fe-09-b7-0f | 0f-34-a2-c1-f4-59
    1 |     0 | d6-31-43-eb-d5-05 | 0f-34-a2-c1-f4-59
    1 |     1 | 0f-34-a2-c1-f4-59 | 77-fe-a6-18-9b-5c

"""
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
    print("{:>5} | {:>5} | {:>12} | {:>12}".format(
          "SWID",
          "LnkID",
          "  DESTMAC   ",
          "   SRCMAC   "))
    print("------|-------|--------------|-------------")

    with open(filename, 'rb') as f:
        raw = f.read(14)
        while raw:
            sw_id, link_id = struct.unpack("BB", raw[0:2])
            #destmac = raw[2:8]

            # struct.unpack doesn't handle 6-byte integers, so we need to
            # pad the first two bytes with 0 to make it 8 bytes 
            destmac = struct.unpack("!Q",  b"\x00\x00" + raw[2:8])[0]
            srcmac = struct.unpack("!Q",  b"\x00\x00" + raw[8:14])[0]
                        
            print("{:5x} | {:5x} | {:012x} | {:012x}".format(
                sw_id,
                link_id,
                destmac,
                srcmac                
            ))
            
            # read next packet
            raw = f.read(14)

if __name__=="__main__":
    if len(sys.argv) == 1:
        print("Usage: ptrace [trace file.out]")
    
    # probably should use argparse here...
    for f in sys.argv[1:]:
        if f.endswith(".out"):
            print_trace(f)
