"""
This is a 2-part protocol sniffer for Lightware Studio.

Use this file on the I2C side, to connect with a physical device

We will send/receive UDP packets to the other half which talks with Lightware Studio
"""

import struct
import smbus2
import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 12345))


response_sizes = {
    0: 16,
    1: 4,
    2: 4,
    3: 16,
    10: 2,
    11: 1,  # undocumented
    66: 1,
    75: 4,
    76: 4,
    78: 1,  # undocumented
    79: 1,
    80: 1,
    82: 1,
    83: 4,
    84: 1,
    85: 4,
    93: 1,
    94: 1,
}

# cmd_id 78 seems to be the one for enabling the serial port

# 78 values (enum):
#    0: "wait for interface"
#    1: "serial mode"
#    2: "i2c mode"
#    3: "serial mode with legacy banner"
#    4: "serial mode with no preamble"


class SF000:
    def __init__(self, busnum, addr):
        self.bus = smbus2.SMBus(busnum)
        self.addr = addr

    def do_read(self, cmd_id, payload):
        print('do_read(%d, %s)' % (cmd_id, payload))
        try:
            num_bytes = response_sizes[cmd_id]
        except KeyError as ke:
            print('dunno the response size:', ke)
            return

        resp = self.bus.read_i2c_block_data(self.addr, cmd_id, num_bytes)
        return bytes(resp)


    def do_write(self, cmd_id, payload):
        print('do_write(%d, %s)' % (cmd_id, payload))
        self.bus.write_i2c_block_data(self.addr, cmd_id, payload)


lidar = SF000(1, 0x66)


while True:
    pkt, addr = sock.recvfrom(1500)
    if pkt is not None and len(pkt) >= 8:
        if pkt[:6] == b'lidar ':
            print(pkt)
            cmd_id = pkt[7]
            payload = pkt[8:]
            if pkt[6] == b'R'[0]:  # do a "read"
                response = lidar.do_read(cmd_id, payload)
                sock.sendto(response, addr)
                
            elif pkt[6] == b'W'[0]:  # do a "write"
                lidar.do_write(cmd_id, payload)
                sock.sendto(b'nothing', addr)
            else:
                print('unknown operation:', chr(pkt[6]))
        else:
            print('unknown packet:', pkt)
    else:
        print('unknown packet:', pkt)
 

