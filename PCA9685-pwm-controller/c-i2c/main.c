
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <linux/i2c-dev.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <sys/time.h>
#include <fcntl.h>

#include "pwm_driver.h"

// The 9685 chip can be at a variety of addresses.  This is the default
// for the Adafruit board:
#define PCA9685_ADDRESS  0x40


void i2c_set_address(int fd, int address) {
	if (ioctl(fd, I2C_SLAVE, address) < 0) {
		perror("i2c_set_address() failed.");
		exit(1);
	}
}


int main(int argc, char** argv) {

	int fd0;
	int i;
	struct timeval tv;

	printf("Hello there.\n");

	fd0 = open("/dev/i2c-1", O_RDWR);

	if (fd0 < 0) {
		perror("i2c_open() failed.");
		exit(1);
	}

	i2c_set_address(fd0, PCA9685_ADDRESS);

	printf("about to call pwm_driver_init()...\n");
	pwm_driver_init(fd0);

	// Some Guy On The Internet (tm) says that 60 Hz is good for servos
	pwm_driver_set_pwm_freq(fd0, 60);

	/*
	for (;;) {
		for (i=70; i<800; ++i) {
			printf("Set: %d\n", i);
			pwm_driver_set_output(fd0, 0, 0, i);
			usleep(1000);
		}
	}
	*/

	for (;;) {
		pwm_driver_set_output(fd0, 0, 0, 100);
		//pwm_driver_set_all_outputs(fd0, 0, 100);
		usleep(500000);
		pwm_driver_set_output(fd0, 0, 0, 400);
		//pwm_driver_set_all_outputs(fd0, 0, 400);
		usleep(500000);
	}

	return 0;
}


