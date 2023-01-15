#ifndef IRRIGATION_H
#define IRRIGATION_H

#include <stdint.h>

uint8_t irrigation_enabled;

void set_irrigation_enabled(uint8_t);

void irrigation_init(void);

void system_error_lock(void);

void irrigation_control(void);

uint8_t irrigation_state(void); 

#endif
