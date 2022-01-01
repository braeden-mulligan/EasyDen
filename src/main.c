#include "arduino_wifi_framework.h"
#include "device_definition.h"
#include "protocol.h"
#include "project_utilities.h"
#include "avr_utilities.h"
#include "avr_adc.h"

#include "ds18b20/ds18b20.h"
#include "ds18b20/romsearch.h"

#include <avr/eeprom.h>
#include <avr/io.h>
#include <stdio.h>
#include <string.h>
#include <util/delay.h>

//TODO: Implement thermostat functionality

#define MAX_SENSOR_COUNT 5

//TODO Pick this based on application loop time.
#define SENSOR_ERROR_COUNT_MAX 15

#define DS18B20_TEMP_SCALE 0.0625

uint8_t sensor_count;
uint8_t sensor_addr[40];

float temperature = 420.0;
float temperature_correction = -0.5;

float humidity = -69.0;
float humidity_correction = -0.08;

uint8_t sensor_error_count = 0;

void measure_temperature(void) {
	float temperature_accum = 0.0;
	uint8_t valid_reads = 0;

	int16_t raw_read;
	uint8_t sensor_error;

	for (uint8_t i = 0; i < sensor_count; ++i) {
		sensor_error = ds18b20read(&PORTB, &DDRB, &PINB, (1 << 0), sensor_addr + (8 * i), &raw_read);
		_delay_ms(1);

		if (sensor_error == DS18B20_ERROR_OK && ((float)raw_read * DS18B20_TEMP_SCALE) < 84.0) {
			temperature_accum += (float)raw_read * DS18B20_TEMP_SCALE;
			++valid_reads;
			if (sensor_error_count > 0) --sensor_error_count;
		} 

		if (sensor_error != DS18B20_ERROR_OK) ++sensor_error_count;

		ds18b20convert(&PORTB, &DDRB, &PINB, (1 << 0), sensor_addr + (8 * i));
		_delay_ms(1);
	}

	if (!valid_reads) {
		return;
	}

	temperature = (temperature_accum / (float)valid_reads) + temperature_correction;
}

void measure_humidity(void) {
	uint16_t raw_read = ADC_read(0);
		
	float max_hum = (3.0 * 1024.0) / 5.0;
	humidity = ((float)raw_read / max_hum) + humidity_correction;
}

void ds18b20_init(void){
	uint8_t retval = DS18B20_ERROR_OTHER;

	for (uint8_t i = 0; i < 3; ++i) {
		retval = ds18b20search(&PORTB, &DDRB, &PINB, (1 << 0), &sensor_count, sensor_addr, sizeof(sensor_addr));
		if (retval == DS18B20_ERROR_OK && sensor_count) break;
		_delay_ms(10);
	}

	if (sensor_count > MAX_SENSOR_COUNT) sensor_count = MAX_SENSOR_COUNT;
}

void sensor_init(void) {
	ADC_init(0);
	_delay_ms(10);
	ds18b20_init();
	measure_temperature();
	measure_humidity();
}

void thermostat_loop() {
	if (!sensor_count) ds18b20_init();

	measure_temperature();
	measure_humidity();

	if (sensor_error_count > SENSOR_ERROR_COUNT_MAX) {
		//TODO: Shut things down and lock up here.
		blink_led(-1, 1000);
	}
}

uint32_t handle_server_get(uint16_t reg) {
	union {
		float sensor_val;
		uint32_t reg_val;
	} value_conv; 

	if (reg == THERMOSTAT_REG_TEMPERATURE) {
		value_conv.sensor_val = temperature;
		return value_conv.reg_val;
	}

	if (reg == THERMOSTAT_REG_HUMIDITY) {
		value_conv.sensor_val = humidity;
		return value_conv.reg_val;
	}

	if (reg == THERMOSTAT_REG_THERMOMETER_COUNT) return (uint32_t)sensor_count;

	return 0;
}

uint32_t handle_server_set(uint16_t reg, uint32_t val) {
	return 0;
}

int main(void) {
	struct wifi_framework_config app_conf = wifi_framework_config_create();

	app_conf.wifi_startup_timeout = 7;
	app_conf.connection_interval = 20;
	app_conf.application_interval = 20;
	app_conf.server_message_get_callback = handle_server_get;
	app_conf.server_message_set_callback = handle_server_set;
	app_conf.app_init_callback = sensor_init;
	app_conf.app_main_callback = thermostat_loop;
	
	wifi_framework_init(&app_conf);

	wifi_framework_start();

	// If here is reached error occurred
	blink_led(-1, 1000);
	
	return 0;
}
