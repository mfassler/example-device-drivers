#ifndef __MPU9250_ACCEL_AND_GRYO
#define __MPU9250_ACCEL_AND_GRYO

extern int read_register(int, char, char*, int);
extern int get_accel_temp_gyro(int, int16_t*, int16_t*, int16_t*);


#endif  // __MPU9250_ACCEL_AND_GRYO
