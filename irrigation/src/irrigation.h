#ifndef IRRIGATION_H
#define IRRIGATION_H

#include <stdint.h>

#define SENSOR_COUNT_MAX 3

uint8_t sensor_count;
uint8_t irrigation_enabled;
uint8_t plant_enable_mask;

float moisture[SENSOR_COUNT_MAX];
float target_moisture[SENSOR_COUNT_MAX];
float moisture_low[SENSOR_COUNT_MAX];
uint16_t moisture_change_hysteresis_time;
uint16_t moisture_change_hysteresis_amount;
// ?? max_water_time
uint32_t min_cooldown_time;
uint32_t moisture_low_delay[SENSOR_COUNT_MAX];
uint16_t sensor_raw[SENSOR_COUNT_MAX];
int16_t sensor_correction[SENSOR_COUNT_MAX];
uint16_t sensor_raw_max[SENSOR_COUNT_MAX];
uint16_t sensor_raw_min[SENSOR_COUNT_MAX];
uint16_t sensor_recorded_max[SENSOR_COUNT_MAX];
uint16_t sensor_recorded_min[SENSOR_COUNT_MAX];

void set_irrigation_enabled(uint8_t);

void irrigation_init(void);

void system_error_lock(void);

void irrigation_control(void);

uint8_t irrigation_state(void); 

#endif
