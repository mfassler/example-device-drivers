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
#include <linux/types.h>
#include <linux/spi/spidev.h>


int read_register(int fd, char reg, char* rx_buffer, int count) {
	char tx_buffer[2];
	int retval;

	tx_buffer[0] = reg;

	retval = write(fd, tx_buffer, 1);

	if (retval != 1) {
		printf("on write(), reval was: %d\n", retval);
		perror("in read_register(), failed to write fd");
		exit(1);
	}

	retval = read(fd, rx_buffer, count);
	if (retval < 0) {
		printf("on read(), retval was: %d\n", retval);
		perror("in read_register(), failed to read fd");
		exit(1);
	}

	return 0;
}


int get_accel_temp_gyro(int fd, int16_t* accel, int16_t* temp, int16_t* gyro) {
	int i;
	int ret;
	uint8_t regNumber;
	char readBuf[14];
	char rx_buffer[2] = {0, 0};

	for (i=0; i<14; i++) {
		regNumber = i + 0x3b;
		ret = read_register(fd, regNumber, rx_buffer, 1);
		readBuf[i] = rx_buffer[0];
	}

	accel[0] = (int16_t)((readBuf[0] << 8) | readBuf[1]);
	accel[1] = (int16_t)((readBuf[2] << 8) | readBuf[3]);
	accel[2] = (int16_t)((readBuf[4] << 8) | readBuf[5]);

	*temp = (int16_t)((readBuf[6] << 8) | readBuf[7]);

	gyro[0] = (int16_t)((readBuf[8] << 8) | readBuf[9]);
	gyro[1] = (int16_t)((readBuf[10] << 8) | readBuf[11]);
	gyro[2] = (int16_t)((readBuf[12] << 8) | readBuf[13]);

	return 0;
}



