#!/usr/bin/env python3

import time
import struct
import smbus2


class DeviceNotFoundError(OSError):
    pass


class BMP390:
    def __init__(self, busnum):
        self._bus = smbus2.SMBus(busnum)
        self._chipAddr = 0x77
        REQUIRED_CHIP_ID = 0x60

        chip_id = self.read_reg_u8(0x00)

        if chip_id != REQUIRED_CHIP_ID:
            raise DeviceNotFoundError(
                'Wrong chip id.  Found: 0x%2x, expecting 0x%2x' % (chip_id, REQUIRED_CHIP_ID))

        print('Found a chip! 0x%2x  :-)' % (chip_id))

        rev_id = self.read_reg_u8(0x01)
        print('rev_id:', rev_id)

        self.read_calibration()

        # Reset the chip:
        self._send_cmd('softreset')

        # Set oversampling:
        self._set_OSR(16, 2)

        # Set IIR filter:
        self._set_iir_filter_coefficient(7)

    def _send_cmd(self, cmd):
        '''
        Send a command to the device
        '''
        commands = {
            'nop': 0x00,
            'fifo_flush': 0xb0,
            'softreset': 0xb6,
        }

        CMD_REGISTER = 0x7e
        self.write_reg_u8(CMD_REGISTER, commands[cmd])

    def _set_iir_filter_coefficient(self, iir_filter_coefficient):
        '''
        Set the IIR filter coefficient
        Valid values are:
            0, 1, 3, 7, 15, 31, 63, 127

        Parameters
        ----------
        iir_filter_coefficient : int
        '''
        iir_choices = {
            0: 0b000,
            1: 0b001,
            3: 0b010,
            7: 0b011,
            15: 0b100,
            31: 0b101,
            63: 0b110,
            127: 0b111,
        }

        val = iir_choices[iir_filter_coefficient] << 1

        CONFIG_REGISTER = 0x1f
        self.write_reg_u8(CONFIG_REGISTER, val)

    def _set_OSR(self, osr_p, osr_t):
        '''
        Set the oversampling rates for pressure and temperature.
        Valid oversampling rates are:
            1, 2, 4, 8, 16, 32

        Parameters
        ----------
        osr_p : int
        osr_t : int
        '''
        # 0x1c -- OSR, oversampling
        #  0b??xxx??? - oversampling of temp data
        #  0b?????xxx - oversampling of pres data
        oversample_choices = {
            1: 0b000,
            2: 0b001,
            4: 0b010,
            8: 0b011,
            16: 0b100,
            32: 0b101,
        }

        val = (oversample_choices[osr_t] << 3) | oversample_choices[osr_p]

        OSR_REGISTER = 0x1c
        self.write_reg_u8(OSR_REGISTER, val)

    def get_temp_and_press(self):

        # Perform one measurement in forced mode
        CONTROL_REGISTER = 0x1b
        self.write_reg_u8(CONTROL_REGISTER, 0x13)

        # 0x03 status register
        #  0bx?xxxxxx - Data ready for temperature sensor
        #  0bxx?xxxxx - Data ready for pressure sensor
        #  0bxxx?xxxx - 0: command in progress, 1: ready for new command

        STATUS_REGISTER = 0x03
        both_complete = 0b01100000  # == 0x60 == 96
        wait_time = 0.002

        # Wait for measurment to complete
        while self.read_reg_u8(STATUS_REGISTER) & both_complete != both_complete:
            time.sleep(wait_time)

        uncomp_temp, uncomp_press = self.read_raw_data()

        temperature = self._compensate_temperature(uncomp_temp)
        pressure = self._compensate_pressure(temperature, uncomp_press)

        return temperature, pressure

    def read_reg_u8(self, reg):
        return self._bus.read_byte_data(self._chipAddr, reg)

    def read_reg_u16(self, reg):
        return self._bus.read_word_data(self._chipAddr, reg)

    # def read_reg_s16(self, reg):
    #    val = self._bus.read_word_data(self._chipAddr, reg)
    #    return convert_u16_to_s16(val)

    def write_reg_u8(self, reg, value):
        return self._bus.write_byte_data(self._chipAddr, reg, value)

    def read_raw_data(self):
        START_REGISTER = 0x04
        NUM_BYTES = 6

        vals = self._bus.read_i2c_block_data(self._chipAddr, START_REGISTER, NUM_BYTES)

        uncomp_press = (vals[2] << 16) | (vals[1] << 8) | vals[0]
        uncomp_temp = (vals[5] << 16) | (vals[4] << 8) | vals[3]

        return uncomp_temp, uncomp_press

    def _compensate_temperature(self, uncomp_temp):
        '''
        This is section 8.5 of the data sheet
        '''
        partial_data1 = uncomp_temp - self._PAR_T1
        partial_data2 = partial_data1 * self._PAR_T2

        self._T_lin = partial_data2 + (partial_data1 * partial_data1) * self._PAR_T3

        return self._T_lin

    def _compensate_pressure(self, T_lin, uncomp_press):
        '''
        This is section 8.6 of the data sheet
        '''
        T = T_lin
        T2 = T_lin ** 2
        T3 = T_lin ** 3

        partial_data1 = self._PAR_P6 * T
        partial_data2 = self._PAR_P7 * T2
        partial_data3 = self._PAR_P8 * T3
        partial_out1 = self._PAR_P5 + partial_data1 + partial_data2 + partial_data3

        partial_data1 = self._PAR_P2 * T
        partial_data2 = self._PAR_P3 * T2
        partial_data3 = self._PAR_P4 * T3
        partial_out2 = uncomp_press * (self._PAR_P1 + partial_data1 + partial_data2 + partial_data3)

        partial_data1 = uncomp_press * uncomp_press
        partial_data2 = self._PAR_P9 + self._PAR_P10 * T
        partial_data3 = partial_data1 * partial_data2
        partial_data4 = partial_data3 + (uncomp_press * uncomp_press * uncomp_press) * self._PAR_P11
        comp_press = partial_out1 + partial_out2 + partial_data4

        return comp_press

    def read_calibration(self):
        '''
        Read the TRIMMING COEFFICIENTS stored on device
        '''
        START_REGISTER = 0x31
        NUM_BYTES = 21
        self.rawBytes = self._bus.read_i2c_block_data(self._chipAddr, START_REGISTER, NUM_BYTES)
        rawBytes = bytearray(self.rawBytes)

        T1, T2, T3, P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11 = \
            struct.unpack("<HHbhhbbHHbbhbb", rawBytes)

        print(T1, T2, T3, P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11)

        # These equations are from Section 8.4 of the datasheet:
        self._PAR_T1 = T1 / 2**-8.0
        self._PAR_T2 = T2 / 2**30.0
        self._PAR_T3 = T3 / 2**48.0

        self._PAR_P1 = (P1 - 2**14.0) / 2**20.0
        self._PAR_P2 = (P2 - 2**14.0) / 2**29.0
        self._PAR_P3 = P3 / 2**32.0
        self._PAR_P4 = P4 / 2**37.0
        self._PAR_P5 = P5 / 2**-3.0
        self._PAR_P6 = P6 / 2**6.0
        self._PAR_P7 = P7 / 2**8.0
        self._PAR_P8 = P8 / 2**15.0
        self._PAR_P9 = P9 / 2**48.0
        self._PAR_P10 = P10 / 2**48.0
        self._PAR_P11 = P11 / 2**65.0

    def print_calibration(self):
        print("t1, t2, t3:")
        print(self._PAR_T1, self._PAR_T2, self._PAR_T3)
        print()

        print(self._PAR_P1, self._PAR_P2)
        print(self._PAR_P3, self._PAR_P4, self._PAR_P5)
        print(self._PAR_P6, self._PAR_P7, self._PAR_P8, self._PAR_P9)
        print(self._PAR_P10, self._PAR_P11)


# This formula is from https://en.wikipedia.org/wiki/Pressure_altitude
def get_altitude(press0, press1):
    K = 44307.7
    return K * (1.0 - float(press1 / press0) ** 0.190284)


bmp = BMP390(1)

# bmp.print_calibration()


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


