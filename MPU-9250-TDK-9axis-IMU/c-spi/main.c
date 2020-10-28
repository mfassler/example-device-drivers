/*
 * This is for use with the MPU-9250 IMU Chip, SPI interface
 *
 * Mode is 1,1  (seems to tolerate 0,0 just fine)
 * Max SPI frequency is 1 MHz
 *
 */

#include <stdint.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/time.h>
#include <linux/types.h>
#include <linux/spi/spidev.h>

#include "mpu9250_accel_and_gyro.h"


static const char *device = "/dev/spidev1.0";
static uint8_t mode = 3;
static uint8_t bits = 8;
static uint32_t speed = 500000;
static uint16_t delay = 1;


#define MPU9250_ID         0x71


int main(int argc, char *argv[]) {
	int ret = 0;
	int fd;

	struct timeval tv;
	int16_t accel[3];
	int16_t temp;
	int16_t gyro[3];

	uint8_t device_id;


	fd = open(device, O_RDWR);
	if (fd < 0) {
		perror("can't open device");
		exit(1);
	}

	// SPI mode
	ret = ioctl(fd, SPI_IOC_WR_MODE, &mode);
	if (ret < 0) {
		perror("can't set spi mode");
		exit(1);
	}

	ret = ioctl(fd, SPI_IOC_RD_MODE, &mode);
	if (ret < 0) {
		perror("can't get spi mode");
		exit(1);
	}


	// bits per word
	ret = ioctl(fd, SPI_IOC_WR_BITS_PER_WORD, &bits);
	if (ret < 0) {
		perror("can't set bits per word");
		exit(1);
	}

	ret = ioctl(fd, SPI_IOC_RD_BITS_PER_WORD, &bits);
	if (ret < 0) {
		perror("can't get bits per word");
		exit(1);
	}


	// max speed Hz
	ret = ioctl(fd, SPI_IOC_WR_MAX_SPEED_HZ, &speed);
	if (ret < 0) {
		perror("can't set max speed hz");
		exit(1);
	}

	ret = ioctl(fd, SPI_IOC_RD_MAX_SPEED_HZ, &speed);
	if (ret < 0) {
		perror("can't get max speed hz");
		exit(1);
	}

	printf("spi mode: %d\n", mode);
	printf("bits per word: %d\n", bits);
	printf("max speed: %d Hz (%d KHz)\n", speed, speed/1000);


	device_id = read_register_byte(fd, 0x75);
	if (device_id != MPU9250_ID) {
		printf("This doesn't seem to be an MPU9250  --  ");
		printf("Expected 0x%x   Recieved: 0x%x\n", MPU9250_ID, device_id);
		exit(1);
	}

	while (1) {

		get_accel_temp_gyro(fd, accel, &temp, gyro);
		gettimeofday(&tv, NULL);

		printf("%ld.%06ld|atg:%d,%d,%d,%d,%d,%d,%d\n",
			tv.tv_sec, tv.tv_usec,
			accel[0], accel[1], accel[2],
			temp,
			gyro[0], gyro[1], gyro[2]);

		usleep(10000);
	}

	close(fd);
	return 0;
}


