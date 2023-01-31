#ifndef IRRIGATION_H
#define IRRIGATION_H

#include <stdint.h>

#define SENSOR_COUNT_MAX 3

typedef enum {
    cal_disabled = 0,
	manual,
	automatic,
	interactive_manual,
	interactive_automatic
} calibration_mode_t;

uint8_t sensor_count;
float moisture[SENSOR_COUNT_MAX];
uint16_t sensor_raw[SENSOR_COUNT_MAX];

// Mostly user settings; non-volatile storage needed.
uint8_t irrigation_enabled;
uint8_t plant_enable_mask;
uint8_t calibration_mode;
float target_moisture[SENSOR_COUNT_MAX];
float moisture_low[SENSOR_COUNT_MAX];
uint32_t moisture_low_delay[SENSOR_COUNT_MAX];
uint16_t moisture_change_hysteresis_time;
uint16_t moisture_change_hysteresis_amount;
uint16_t sensor_raw_max[SENSOR_COUNT_MAX];
uint16_t sensor_raw_min[SENSOR_COUNT_MAX];
uint16_t sensor_recorded_max[SENSOR_COUNT_MAX];
uint16_t sensor_recorded_min[SENSOR_COUNT_MAX];

void set_irrigation_enabled(uint8_t setting);

void set_plant_enable(uint8_t bitmask);

void set_calibration_mode(uint8_t setting, uint8_t plant_select);

void set_target_moisture(uint8_t plant_select, float value);

void set_moisture_low(uint8_t plant_select, float value);

void set_moisture_low_delay(uint8_t plant_select, uint32_t time_s);

void set_sensor_raw_max(uint8_t plant_select, uint16_t value);

void set_sensor_raw_min(uint8_t plant_select, uint16_t value);

void set_moisture_change_hysteresis_time(uint16_t time_s);

void set_moisture_change_hysteresis_amount(uint16_t sensor_raw_delta);

// TODO: For debugging? 
void switch_pump(uint8_t setting);

void irrigation_init(void);

void system_error_lock(void);

void irrigation_control(void);

void reset_configurations(uint8_t plant_select_mask);

#endif
