
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <math.h>


// Some of this code was copied-from / inspired-by the Adafruit python
// library: 
//     https://github.com/adafruit/Adafruit_Python_PCA9685
//     file:  Adafruit_PCA9685/PCA9685.py


// Registers:
#define MODE1            0x00
#define MODE2            0x01
#define SUBADR1          0x02
#define SUBADR2          0x03
#define SUBADR3          0x04
#define PRESCALE         0xFE
#define LED0_ON_L        0x06
#define LED0_ON_H        0x07
#define LED0_OFF_L       0x08
#define LED0_OFF_H       0x09
#define ALL_LED_ON_L     0xFA
#define ALL_LED_ON_H     0xFB
#define ALL_LED_OFF_L    0xFC
#define ALL_LED_OFF_H    0xFD

// Bits:
#define RESTART          0x80
#define SLEEP            0x10
#define ALLCALL          0x01
#define INVRT            0x10
#define OUTDRV           0x04


int _device_write8(int fd, unsigned char reg, unsigned char value) {
	int retval;
	char writeBuf[2];

	writeBuf[0] = reg;
	writeBuf[1] = value;

	retval = write(fd, writeBuf, 2);
	if (retval != 2) {
		printf("Error: pwm_driver_set_output(), on write(), retval was: %d\n", retval);
		return retval;
	}

	return 0;
}

int _device_read8(int fd, unsigned char reg) {
	int retval;
	char writeBuf[1];
	char readBuf[1];

	writeBuf[0] = reg;

	retval = write(fd, writeBuf, 1);
	if (retval != 1) {
		printf("Error: pwm_driver_set_output(), on write(), retval was: %d\n", retval);
		return retval;
	}

	retval = read(fd, readBuf, 1);
	if (retval < 0) {
		printf("on read(), retval was: %d\n", retval);
		return retval;
	}

	return (int) readBuf[0];
}


int pwm_driver_init(int fd) {
	int retval;

	int mode1;
	int mode2;
	int prescale;


	mode1 = _device_read8(fd, MODE1);
	printf("mode1 register is: 0x%x\n", mode1);

	prescale = _device_read8(fd, PRESCALE);
	printf("prescale is: 0x%x\n", prescale);

	_device_write8(fd, MODE2, OUTDRV);
	_device_write8(fd, MODE1, ALLCALL);
	usleep(5000); // wait for oscillator

	mode1 = _device_read8(fd, MODE1);
	mode1 &= ~SLEEP;  // wake up (reset sleep)
	_device_write8(fd, MODE1, mode1);
	usleep(5000); // wait for oscillator

	return 0;
}


void pwm_driver_set_pwm_freq(int fd, float freq_hz) {
	float prescaleval;
	int prescale;
	int oldmode, newmode;

	prescale = round(25000000.0 / 4096 / freq_hz - 1.0);

	printf("Requested freq: %f\n", freq_hz);
	printf("Calculated prescale: %d\n", prescale);

	oldmode = _device_read8(fd, MODE1);
	newmode = (oldmode & 0x7f) | 0x10;  // sleep
	_device_write8(fd, MODE1, newmode); // go to sleep
	_device_write8(fd, PRESCALE, prescale);
	_device_write8(fd, MODE1, oldmode);
	usleep(5000); // wait for oscillator if waking up
	_device_write8(fd, MODE1, oldmode | 0x80);  // restart enabled

	prescale = _device_read8(fd, PRESCALE);
	printf("Prescale is: %d\n", prescale);
}



void pwm_driver_set_output(int fd, int channel, int on_value, int off_value) {

	//printf("Setting channel %d to %d on, %d off\n", channel, on_value, off_value);

	_device_write8(fd, LED0_ON_L + 4*channel, on_value & 0xff);
	_device_write8(fd, LED0_ON_H + 4*channel, (on_value >> 8) & 0x0f);
	_device_write8(fd, LED0_OFF_L + 4*channel, off_value & 0xff);
	_device_write8(fd, LED0_OFF_H + 4*channel, (off_value >> 8) & 0x0f);
}


void pwm_driver_set_all_outputs(int fd, int on_value, int off_value) {
	_device_write8(fd, ALL_LED_ON_L, on_value & 0xff);
	_device_write8(fd, ALL_LED_ON_H, (on_value >> 8) & 0x0f);
	_device_write8(fd, ALL_LED_OFF_L, off_value & 0xff);
	_device_write8(fd, ALL_LED_OFF_H, (off_value >> 8) & 0x0f);
}
