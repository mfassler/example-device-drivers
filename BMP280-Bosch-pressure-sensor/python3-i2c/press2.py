#!/usr/bin/env python3

import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

import os
import time
#import smbus2


def convert_u16_to_s16(val):
    return (val + 2**15) % 2**16 - 2**15

class BMP280:
    def __init__(self, busnum=0):
        pass

    def read_raw_data(self):
        p1 = self.read_reg_u8(0xf7)
        p2 = self.read_reg_u8(0xf8)
        p3 = self.read_reg_u8(0xf9)
        uncomp_press = (p1 << 12) | (p2 << 4) | (p3 >> 4)

        t1 = self.read_reg_u8(0xfa)
        t2 = self.read_reg_u8(0xfb)
        t3 = self.read_reg_u8(0xfc)
        uncomp_temp = (t1 << 12) | (t2 << 4) | (t3 >> 4)

        return uncomp_temp, uncomp_press


    def _compensate_temperature(self, adc_T):
        var1 = (adc_T/16384.0 - self._dig_T1/1024.0) * (self._dig_T2)
        var2 = ((adc_T/131072.0 - self._dig_T1/8192.0) * adc_T/131072.0 - self._dig_T1/8192.0) * self._dig_T3
        self._t_fine = (var1 + var2);
        T = (var1 + var2) / 5120.0
        return T


    def _compensate_pressure(self, adc_P):
        #double var1, var2, p;
        var1 = self._t_fine/2.0 - 64000.0
        var2 = var1 * var1 * self._dig_P6 / 32768.0
        var2 = var2 + var1 * self._dig_P5 * 2.0
        var2 = var2/4.0 + self._dig_P4 * 65536.0
        var1 = (self._dig_P3 * var1 * var1 / 524288.0 + self._dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self._dig_P1

        if var1 == 0.0:
            return 0  # avoid exception caused by division by zero

        p = 1048576.0 - adc_P
        p = (p - var2 / 4096.0) * 6250.0 / var1
        var1 = self._dig_P9 * p * p / 2147483648.0
        var2 = p * self._dig_P8 / 32768.0
        p = p + (var1 + var2 + self._dig_P7) / 16.0
        return p


    def get_temp(self):
        ut = self.read_raw_data()
        return self._compensate_temperature(ut)

    def get_temp_and_press(self):
        ut, up = self.read_raw_data()
        T = self._compensate_temperature(ut)
        P = self._compensate_pressure(up)
        return T, P

    def read_calibration(self):
        self._dig_T1 = 27452
        self._dig_T2 = 25554
        self._dig_T3 = 50
        self._dig_P1 = 38774
        self._dig_P2 = -10698
        self._dig_P3 = 3024
        self._dig_P4 = 7668
        self._dig_P5 = -186
        self._dig_P6 = -7
        self._dig_P7 = 15500
        self._dig_P8 = -14600
        self._dig_P9 = 6000


    def print_calibration(self):
        print(self._dig_T1)
        print(self._dig_T2)
        print(self._dig_T3)
        print(self._dig_P1)
        print(self._dig_P2)
        print(self._dig_P3)
        print(self._dig_P4)
        print(self._dig_P5)
        print(self._dig_P6)
        print(self._dig_P7)
        print(self._dig_P8)
        print(self._dig_P9)



def get_altitude(press0, press1):
    K = 44330.0
    #p_0 = 101695.0
    p_0 = press0
    return K * (1.0 - (float(press1) / p_0) ** (1/5.255))



bmp = BMP280(1)

bmp.read_calibration()
bmp.print_calibration()


p_0 = None
while True:
    T, P = bmp.get_temp_and_press()
    if p_0 is None:
        p_0 = P
        alt = 0.0
    else:
        alt = get_altitude(p_0, P)

    print("%.02f %.03f %.03f" % (T, P, alt))
    time.sleep(0.5)



