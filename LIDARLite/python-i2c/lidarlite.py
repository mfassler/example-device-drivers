
import sys
import time
import smbus2


class LidarLite:
    def __init__(self, busnum, chipAddr):
        self._bus = smbus2.SMBus(busnum)
        self._chipAddr = chipAddr

    def read_reg_u8(self, reg):
        return self._bus.read_byte_data(self._chipAddr, reg)

    def write_reg_u8(self, reg, value):
        return self._bus.write_byte_data(self._chipAddr, reg, value)

    def acq_command(self, cmd):
        # Valid commands:
        # 0x00 - reset
        # 0x03 - take distance measurement without receiver bias correction
        # 0x04 - take distance measurement with receiver bias correction
        self.write_reg_u8(0x00, cmd)

    def get_distance(self):
        self.acq_command(4)

        # Wait for device to become ready:
        while True:
            status = self.read_reg_u8(0x01)
            if status & 0x01 == 0:
                break
            time.sleep(0.01)

        vals = self._bus.read_i2c_block_data(self._chipAddr, 0x8f, 2)
        dist_in_cm = vals[0] << 8 | vals[1]
        return dist_in_cm


if __name__ == '__main__':
    lidar = LidarLite(int(sys.argv[1]), 0x62)

    while True:
        dist_in_cm = lidar.get_distance()
        print(dist_in_cm)


