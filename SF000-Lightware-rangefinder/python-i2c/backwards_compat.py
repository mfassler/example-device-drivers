
import time
import struct
import smbus2


class SF000:
    def __init__(self, busnum, addr):
        self.bus = smbus2.SMBus(busnum)
        self.addr = addr

    def backwards_compat_read(self):
        pkt = self.bus.read_i2c_block_data(self.addr, 0, 2)
        dist_in_cm = pkt[0] << 8 | pkt[1]
        return dist_in_cm


lidar = SF000(1, 0x66)


while True:
    dist_in_cm = lidar.backwards_compat_read()
    print(dist_in_cm)
    time.sleep(0.05)


