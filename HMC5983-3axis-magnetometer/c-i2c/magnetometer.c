
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>

// Device ID should be "H43"
// this is true for both the HMC5983 (inside the HolyBro GPS module)
// and the magnetometer component of the LSM303 found in the 
// Adafruit 10dof module
const char DEVICE_ID[] = "H43";



ssize_t read_register(int fd, uint8_t reg, char* rx_buffer, size_t count) {
	char tx_buffer[2];
	ssize_t retval;

	tx_buffer[0] = reg;

	retval = write(fd, tx_buffer, 1);

	if (retval != 1) {
		printf("on write(), reval was: %ld\n", retval);
		perror("in read_register(), failed to write fd");
		exit(1);
	}

	retval = read(fd, rx_buffer, count);
	if (retval < 0) {
		printf("on read(), retval was: %ld\n", retval);
		perror("in read_register(), failed to read fd");
		exit(1);
	}

	return 0;
}


#define VENDOR_ID 0x48
#define DEVICE_ID 0x09

int magnet_init(int fd) {
	int retval;
	char writeBuf[2];
	char readBuf[3];

	retval = read_register(fd, 0x00, readBuf, 1);
	if (readBuf[0] != VENDOR_ID) {
		perror("This doesn't seem to be an AK09916");
		return -1;
	}

	retval = read_register(fd, 0x01, readBuf, 1);
	if (readBuf[0] != DEVICE_ID) {
		perror("This doesn't seem to be an AK09916");
		return -1;
	}

	retval = read_register(fd, 0x31, readBuf, 1);
	printf("register 0x31:  0x%x\n", readBuf[0]);


	// Set the mode:
	// 0x00 - sleep
	// 0x02, Mode 1: 10Hz continuous
	// 0x04, Mode 2: 20Hz continuous
	// 0x06, Mode 3: 50Hz continuous
	// 0x08, Mode 4: 100Hz continuous
	// 
	writeBuf[0] = 0x31;
	writeBuf[1] = 0x04;
	retval = write(fd, writeBuf, 2);

	retval = read_register(fd, 0x31, readBuf, 1);
	printf("register 0x31:  0x%x\n", readBuf[0]);

	return 0;
}



int magnet_take_sample(int fd, int16_t *xyz) {
	int retval;

	retval = read_register(fd, 0x11, (char*)xyz, 6);

/*
	char readBuf[6];

	retval = read_register(fd, 0x11, readBuf, 6);

	xyz[0] = (int16_t)readBuf[0] | (int16_t)(readBuf[1] << 8);
	xyz[1] = (int16_t)readBuf[2] | (int16_t)(readBuf[3] << 8);
	xyz[2] = (int16_t)readBuf[4] | (int16_t)(readBuf[5] << 8);
*/
	return 0;
}


