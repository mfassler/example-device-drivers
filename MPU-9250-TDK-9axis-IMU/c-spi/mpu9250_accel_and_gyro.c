
/*
 * This is for use with the MPU-9250 IMU Chip, SPI interface
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


static uint8_t bits = 8;
static uint32_t speed = 500000;
static uint16_t delay = 1;


uint8_t read_register_byte(int fd, uint8_t reg_number) {
	unsigned char tx_buffer[2];
	unsigned char rx_buffer[2];
	int ret;

	tx_buffer[0] = 0x80 | reg_number; // setting msb to 1 makes this a "read" operation

	struct spi_ioc_transfer tr = {
		.tx_buf = (unsigned long)tx_buffer,
		.rx_buf = (unsigned long)rx_buffer,
		.len = 2,
		.delay_usecs = delay,
		.speed_hz = speed,
		.bits_per_word = bits,
	};

	ret = ioctl(fd, SPI_IOC_MESSAGE(1), &tr);
	if (ret < 1) {
		perror("can't send spi message");
		exit(1);
	}

	return rx_buffer[1];
}


int get_accel_temp_gyro(int fd, int16_t* accel, int16_t* temp, int16_t* gyro) {
	int i;
	int ret;
	uint8_t regNumber;
	char readBuf[14];

	for (i=0; i<14; i++) {
		regNumber = i + 0x3b;
		readBuf[i] = read_register_byte(fd, regNumber);
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



