#ifndef __MPU9250_ACCEL_AND_GRYO
#define __MPU9250_ACCEL_AND_GRYO

extern uint8_t read_register_byte(int, uint8_t);
extern int get_accel_temp_gyro(int, int16_t*, int16_t*, int16_t*);


#endif  // __MPU9250_ACCEL_AND_GRYO
