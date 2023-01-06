
import time
import struct
import smbus2


class TFmini:
    def __init__(self, busnum, addr):
        self._bus = smbus2.SMBus(busnum)
        self._chip_addr = addr

    def read_reg(self, reg: int, dlen: int) -> bytes:
        pkt = reg.to_bytes(2, 'big') + dlen.to_bytes(1, 'big')
        msg1 = smbus2.i2c_msg.write(self._chip_addr, pkt)
        msg2 = smbus2.i2c_msg.read(self._chip_addr, dlen)
        self._bus.i2c_rdwr(msg1, msg2)
        return bytes(msg2)

    def write_reg(self, reg: int, value: bytes):
        dlen = len(value)
        pkt1 = reg.to_bytes(2, 'big') + dlen.to_bytes(1, 'big')
        msg1 = smbus2.i2c_msg.write(self._chip_addr, pkt1)
        pkt2 = value
        msg2 = smbus2.i2c_msg.write(self._chip_addr, pkt2)
        self._bus.i2c_rdwr(msg1, msg2)

    def get_range(self):
        pkt = self.read_reg(0x0102, 7)
        # My pdf doesn't seem to quite match my device...
        trigger_done, whut, dist, strength, mode = struct.unpack('<BBHHB', pkt)

        print(trigger_done, whut, dist, strength, mode)


if __name__ == '__main__':

    lidar = TFmini(1, 0x10)

    while True:
        lidar.get_range()
        time.sleep(0.1)
