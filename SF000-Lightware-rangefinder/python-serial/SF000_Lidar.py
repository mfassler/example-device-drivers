
import threading
import serial
import struct

from createCRC import createCRC


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


class SF000_Lidar:
    def __init__(self, portname, baudrate=115200):
        self._ser = serial.Serial(portname, baudrate, timeout=0.1)
        self._t1 = threading.Thread(target=self.reading_task)
        self._t1.start()

    def reading_task(self):
        while True:
            ch0 = self._ser.read(1)
            if ch0 is None:
                pass
            elif ch0 == b'':
                pass
            elif ch0 == b'\xaa':
                flag_bytes = self._ser.read(2)
                flags, = struct.unpack('<H', flag_bytes)
                plen = flags >> 6

                cmd_id = self._ser.read(1)
                payload = self._ser.read(plen - 1)

                pkt_crc, = struct.unpack('<H', self._ser.read(2))
                to_check = ch0 + flag_bytes + cmd_id + payload
                calc_crc = createCRC(to_check)

                if pkt_crc == calc_crc:
                    self.rx_packet(cmd_id[0], payload)
                else:
                    print('bad CRC')

            else:
                print('invalid start byte:', ch0)

    def rx_packet(self, cmd_id, payload):
        if cmd_id == 0:
            if len(payload) == 16:
                self.rx_product_name(payload)
            else:
                print('PROTOCOL ERROR: product name, wrong length: %d bytes' % (len(payload)))
        elif cmd_id == 1:
            if len(payload) == 4:
                self.rx_hardware_version(payload)
            else:
                print('PROTOCOL ERROR: hardware version, wrong length: %d bytes' % (len(payload)))
        elif cmd_id == 2:
            if len(payload) == 4:
                self.rx_firmware_version(payload)
            else:
                print('PROTOCOL ERROR: firmware version, wrong length: %d bytes' % (len(payload)))
        elif cmd_id == 3:
            if len(payload) == 16:
                self.rx_serial_number(payload)
            else:
                print('PROTOCOL ERROR: serial number, wrong length: %d bytes' % (len(payload)))
        elif cmd_id == 44:
            self.rx_distance_data_in_cm(payload)
        else:
            print('rx CMD: %d,  %d bytes' % (cmd_id, len(payload)))

    def request_product_name(self):
        cmd_id = 0
        data = b''
        pkt = make_packet(cmd_id, data)
        self._ser.write(pkt)

    def rx_product_name(self, payload):
        self.product_name = payload
        print('Product name:', payload)

    def request_hardware_version(self):
        cmd_id = 1
        data = b''
        pkt = make_packet(cmd_id, data)
        self._ser.write(pkt)

    def rx_hardware_version(self, payload):
        self.hardware_version, = struct.unpack('<L', payload)
        print('hardware version:', self.hardware_version)

    def request_firmware_version(self):
        cmd_id = 2
        data = b''
        pkt = make_packet(cmd_id, data)
        self._ser.write(pkt)

    def rx_firmware_version(self, payload):
        patch, minor, major, reserved = struct.unpack('<BBBB', payload)
        self.firmware_version = major, minor, patch
        print('firmware version:', major, minor, patch)

    def request_serial_number(self):
        cmd_id = 3
        data = b''
        pkt = make_packet(cmd_id, data)
        self._ser.write(pkt)

    def rx_serial_number(self, payload):
        self.serial_number = payload
        print('serial number:', payload)

    def request_stream(self):
        cmd_id = 30
        data = struct.pack('<L', 5)
        pkt = make_packet(cmd_id, data, write=True)
        self._ser.write(pkt)

    def rx_distance_data_in_cm(self, payload):
        first_return_raw, = struct.unpack('<H', payload[:2])
        print(first_return_raw)



