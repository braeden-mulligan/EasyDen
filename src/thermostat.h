#ifndef THERMOSTAT_H
#define THERMOSTAT_H

#include <stdint.h>

float temperature;
float humidity;
uint8_t humidity_sensor_count;

// Configurables
uint8_t thermostat_enabled;
float target_temperature;
float temperature_correction;
float threshold_high;
float threshold_low;
float humidity_correction;
uint16_t max_heat_time;
uint16_t min_cooldown_time;

// Make available for metrics
uint8_t thermostat_state(void);
uint16_t heater_triggered_count;
uint16_t cooldown_triggered_count;
uint16_t sensor_error_total;

void thermostat_init(void);

void thermostat_control(void);

void set_thermostat_enabled(uint8_t);

void set_target_temperature(float);

void set_temperature_correction(float);

void set_threshold_high(float);

void set_threshold_low(float);

void set_humidity_correction(float);

void set_max_heat_time(uint16_t);

void set_min_cooldown_time(uint16_t);

#endif
