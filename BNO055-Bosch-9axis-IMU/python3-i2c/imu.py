#!/usr/bin/env python3

import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

import os
import time
import smbus2


def convert_u16_to_s16(val):
    return (val + 2**15) % 2**16 - 2**15

def convert_2_bytes_to_s16(MSB, LSB):
    uval = (MSB << 8) | LSB
    return convert_u16_to_s16(uval)


class BNO055:
    def __init__(self, busnum):
        self._bus = smbus2.SMBus(busnum)
        self._chipAddr = 0x28
        chip_id = self.read_reg_u8(0x00)
        if chip_id == 0xa0:
            print('Found a chip! :-)')
        else:
            print('wrong chip id')
        self._chipId = chip_id
        self._acc_id = self.read_reg_u8(0x01)
        self._mag_id = self.read_reg_u8(0x02)
        self._gyr_id = self.read_reg_u8(0x03)
        self._sw_rev_id_lsb = self.read_reg_u8(0x04)
        self._sw_rev_id_msb = self.read_reg_u8(0x05)
        self._bl_ref_id = self.read_reg_u8(0x06)
        print('Chip ID: 0x%02x' % (self._chipId)) # expecting 0xa0
        print('ACC ID: 0x%02x' % (self._acc_id)) # expecting 0xfb
        print('MAG ID: 0x%02x' % (self._mag_id)) # expecting 0x32
        print('GYR ID: 0x%02x' % (self._gyr_id)) # expecting 0x0f

        # The next 3 are software revisions, and can vary:
        print('sw lsb: 0x%02x' % (self._sw_rev_id_lsb))
        print('sw msb: 0x%02x' % (self._sw_rev_id_msb))
        print('bl ref id: 0x%02x' % (self._bl_ref_id))

    def get_accel(self):
        data = self._bus.read_i2c_block_data(self._chipAddr, 0x08, 6)
        accel_x = convert_2_bytes_to_s16(data[1], data[0])
        accel_y = convert_2_bytes_to_s16(data[3], data[2])
        accel_z = convert_2_bytes_to_s16(data[5], data[4])
        return [accel_x, accel_y, accel_z]


    def read_reg_u8(self, reg):
        return self._bus.read_byte_data(self._chipAddr, reg)

    def read_reg_u16(self, reg):
        return self._bus.read_word_data(self._chipAddr, reg)

    def read_reg_s16(self, reg):
        val = self._bus.read_word_data(self._chipAddr, reg)
        return convert_u16_to_s16(val)

    def write_reg_u8(self, reg, value):
        return self._bus.write_byte_data(self._chipAddr, reg, value)


    def read_raw_data(self):
        pass



'''
# Interesting R/W Registers:
0x40 - TEMP_SOURCE, only the 2 lsbs
0x3e - PWR_MODE, only the 2 lsbs
0x3d - OPR_MODE, only the 4 lsbs
         0x00 - config mode

         0x01 - ACC only
         0x02 - MAG only
         0x03 - GYRO only
         0x04 - ACC and MAG
         0x05 - ACC and GYRO
         0x06 - MAG and GYRO
         0x07 - ACC and MAG and GYRO

         0x08 - Fusion, IMU
         0x09 - Fusion, Compass
         0x0a - Fusion, M4G (Magnet for Gyroscope)
         0x0b - Fusion, NDOF_FMC_OFF
         0x0c - Fusion, NDOF

0x3b - UNIT_SEL

... ACC_Config, GYR_Config, MAG_Config...
'''


imu = BNO055(1)

## 0x3d is OPR_MODE
imu.write_reg_u8(0x3d, 0x00) # set to config mode
imu.write_reg_u8(0x3d, 0x07) # set to non-fusion mode, all sensors on
imu.read_reg_u8(0x3d)


while True:
    print(imu.get_accel())
    time.sleep(0.25)



