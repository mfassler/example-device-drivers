
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <linux/i2c-dev.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <sys/time.h>
#include <fcntl.h>


#include "magnetometer.h"

#define ADDR_MAGNETOMETER 0x0c


// The HMC5983 seems to be identical to the magnetometer component
// found in the LSM303 which is the accel+magnet chip used
// in the Adafruit 10dof



void i2c_set_address(int fd, int address) {
	if (ioctl(fd, I2C_SLAVE, address) < 0) {
		perror("i2c_set_address() failed.");
		exit(1);
	}
}


int main(int argc, char** argv) {

	int fd0;
	struct timeval tv;
	int16_t magnet_xyz[] = {0, 0, 0};

	printf("Hello there.\n");

	fd0 = open("/dev/i2c-1", O_RDWR);

	if (fd0 < 0) {
		perror("i2c_open() failed.");
		exit(1);
	}

	i2c_set_address(fd0, ADDR_MAGNETOMETER);
	printf("about to call magnet_init()...\n");
	magnet_init(fd0);

	for (;;) {
		gettimeofday(&tv, NULL);
		magnet_take_sample(fd0, magnet_xyz);

		printf("t: %ld.%06ld, magnet: %d, %d, %d\n",
		       tv.tv_sec, tv.tv_usec, magnet_xyz[0], magnet_xyz[1], magnet_xyz[2]);

		//getchar(); // wait for ENTER
		usleep(50000); // 20Hz
	}

	return 0;
}


