
import time
import struct
import smbus2


class SF000:
    def __init__(self, busnum, addr):
        self.bus = smbus2.SMBus(busnum)
        self.addr = addr

    def get_product_name(self):
        pkt = self.bus.read_i2c_block_data(self.addr, 0, 16)
        product_name = bytes(pkt)
        print(product_name)

    def get_hardware_version(self):
        pkt = self.bus.read_i2c_block_data(self.addr, 1, 4)
        hardware_version, = struct.unpack('<L', bytes(pkt))
        print(hardware_version)

    def get_firmware_version(self):
        pkt = self.bus.read_i2c_block_data(self.addr, 2, 4)
        patch = pkt[0]
        minor = pkt[1]
        major = pkt[2]
        resvd = pkt[3]  # reserved
        print("Firmare: %d.%d.%d" % (major, minor, patch))

    def get_serial_number(self):
        pkt = self.bus.read_i2c_block_data(self.addr, 3, 16)
        serial_number = bytes(pkt)
        print(serial_number)

    def get_distance_data_in_cm(self):
        num_bytes = 8  # TODO:  this can vary, I guess?
        # TODO:  8 int16's, so 16 bytes
        pkt = self.bus.read_i2c_block_data(self.addr, 44, num_bytes)
        dist, = struct.unpack('<h', bytes(pkt[:2]))

        return dist


lidar = SF000(1, 0x66)

lidar.get_product_name()
lidar.get_hardware_version()
lidar.get_firmware_version()
lidar.get_serial_number()

while True:
    dist_in_cm = lidar.get_distance_data_in_cm()
    print(dist_in_cm)
    time.sleep(0.05)


