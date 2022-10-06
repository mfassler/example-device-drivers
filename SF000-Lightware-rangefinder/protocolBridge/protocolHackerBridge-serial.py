"""
This is a 2-part protocol sniffer for Lightware Studio.

Use this file on the serial-port side, to connect with Lightware Studio.

We will send/receive UDP packets to the other half which talks to the i2c device.
"""

import socket
import serial
import struct

from createCRC import createCRC

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 0))
REMOTE_ADDR = ('192.168.1.4', 12345)


def make_packet(cmd_id, data, write=False):

    payload = bytes([cmd_id]) + data
    plen = len(payload)
    flags = plen << 6
    if write:
        flags |= 0x0001  # set the write bit
    header = struct.pack('<BH', 0xaa, flags)

    header_and_payload = header + payload

    crc = createCRC(header_and_payload)
    crc = struct.pack('<H', crc)

    return header_and_payload + crc


def make_udp_packet(do_write: bool, cmd_id: int, payload: bytes) -> bytes:
    if do_write:
        header = b'lidar W' + bytes([cmd_id])
    else:
        header = b'lidar R' + bytes([cmd_id])

    return header + payload



ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.3)

while True:
    ch0 = ser.read(1)
    if ch0 is None:
        pass
    elif ch0 == b'':
        pass
    elif ch0 == b'\xaa':
        flag_bytes = ser.read(2)
        flags, = struct.unpack('<H', flag_bytes)
        do_write = bool(flags & 0x0001)
        plen = flags >> 6

        cmd_id = ser.read(1)
        payload = ser.read(plen - 1)

        pkt_crc, = struct.unpack('<H', ser.read(2))
        to_check = ch0 + flag_bytes + cmd_id + payload
        calc_crc = createCRC(to_check)

        if pkt_crc == calc_crc:
            cmd_id = cmd_id[0]  # convert a "bytes" to uint8
            print('serial port:', do_write, cmd_id, payload)
            udpPkt = make_udp_packet(do_write, cmd_id, payload)
            sock.sendto(udpPkt, REMOTE_ADDR)
            respPkt, addr = sock.recvfrom(1500)
            if not do_write:
                serPkt = make_packet(cmd_id, respPkt)
                ser.write(serPkt)
            else:
                serPkt = make_packet(cmd_id, b'', write=True)
                ser.write(serPkt)

            print('udp response:', respPkt)

        else:
            print('bad CRC')

    else:
        print('invalid start byte:', ch0)


