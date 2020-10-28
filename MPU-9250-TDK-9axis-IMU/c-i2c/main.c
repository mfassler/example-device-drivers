/*
 * This is for use with the MPU-9250 (or -9255) IMU Chip, i2c interface
 *
 */

#include <stdint.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

#include "mpu9250_accel_and_gyro.h"


static const char *device = "/dev/i2c-1";

#define MPU9250_ADDRESS0            0x68
//#define MPU9250_ADDRESS1            0x69

#define MPU9250_ID                  0x71
#define MPU9255_ID                  0x73


void i2c_set_address(int fd, int address) {
	if (ioctl(fd, I2C_SLAVE, address) < 0) {
		perror("i2c_set_address() failed.");
		exit(1);
	}
}


int main(int argc, char *argv[]) {
	int ret = 0;
	int fd0;

	int16_t accel[3];
	int16_t temp;
	int16_t gyro[3];

	char rx_buffer[2] = {0, 0};

	fd0 = open(device, O_RDWR);
	if (fd0 < 0) {
		perror("open(device) failed");
		exit(1);
	}

	i2c_set_address(fd0, MPU9250_ADDRESS0);

	ret = read_register(fd0, 0x75, rx_buffer, 1);
	printf("rx[0]: 0x%x\n", rx_buffer[0]);

	switch (rx_buffer[0]) {
	case MPU9250_ID:
		printf("found an MPU-9250\n");
		break;
	case MPU9255_ID:
		printf("found an MPU-9255\n");
		break;
	default:
		printf("Unknown device ID: 0x%02x\n", rx_buffer[0]);
		exit(1);
	}


	while(1) {

		get_accel_temp_gyro(fd0, accel, &temp, gyro);

		printf("accel, temp, gyro: %d, %d, %d, %d, %d, %d, %d\n",
			accel[0], accel[1], accel[2],
			temp,
			gyro[0], gyro[1], gyro[2]);

		usleep(50000);
	}

	close(fd0);
	return ret;
}


