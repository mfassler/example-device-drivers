#ifndef __PWM_DRIVER_H
#define __PWM_DRIVER_H

extern int pwm_driver_init(int);
extern void pwm_driver_set_pwm_freq(int, float);
extern void pwm_driver_set_output(int, int, int, int);
extern void pwm_driver_set_all_outputs(int, int, int);


#endif // __PWM_DRIVER_H

