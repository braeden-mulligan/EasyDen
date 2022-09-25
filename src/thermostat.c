#include "thermostat.h"

#include "avr_adc.h"
#include "avr_utilities.h"
#include "avr_timer_util.h"
#include "device_definition.h"
#include "nano_configs_eeprom_offsets.h"
#include "ds18b20/ds18b20.h"
#include "ds18b20/romsearch.h"

#include <avr/eeprom.h>
#include <avr/io.h>
#include <util/delay.h>

#define MEM_ENABLE 512
#define MEM_TARGET_TEMPERATURE (MEM_ENABLE + sizeof(thermostat_enabled))
#define MEM_TEMPERATURE_CORRECTION (MEM_TARGET_TEMPERATURE + sizeof(target_temperature))
#define MEM_THRESHOLD_HIGH (MEM_TEMPERATURE_CORRECTION + sizeof(temperature_correction))
#define MEM_THRESHOLD_LOW (MEM_THRESHOLD_HIGH + sizeof(threshold_high))
#define MEM_HUMIDITY_CORRECTION (MEM_THRESHOLD_LOW + sizeof(threshold_low))
#define MEM_MAX_HEAT_TIME (MEM_HUMIDITY_CORRECTION + sizeof(humidity_correction))
#define MEM_MIN_COOLDOWN_TIME (MEM_MAX_HEAT_TIME + sizeof(max_heat_time))

#define heater_active (!!(PORTD & (1 << PD4)))

#define MIN_THRESHOLD 0.15

#define MAX_SENSOR_COUNT 5

//TODO Pick this based on application loop time.
#define SENSOR_ERROR_COUNT_MAX 15
#define SENSOR_ERROR_RECOVERY_HYSTERESIS (SENSOR_ERROR_COUNT_MAX + 5)

#define DS18B20_TEMP_SCALE 0.0625

enum {
	OFF = 0,
	ON
};

uint8_t sensor_count;

uint8_t sensor_addr[40];

uint8_t sensor_error_tally;

uint8_t humidity_sensor_initialized;

uint8_t cooldown_active;
// -----

void measure_temperature(void) {
	float temperature_sum = 0.0;
	uint8_t valid_reads = 0;

	int16_t raw_read;
	uint8_t sensor_error;

	for (uint8_t i = 0; i < sensor_count; ++i) {
		_delay_ms(1);
		sensor_error = ds18b20read(&PORTB, &DDRB, &PINB, (1 << 0), sensor_addr + (8 * i), &raw_read);

		if (sensor_error == DS18B20_ERROR_OK && ((float)raw_read * DS18B20_TEMP_SCALE) < 84.0) {
			temperature_sum += (float)raw_read * DS18B20_TEMP_SCALE;
			++valid_reads;
			if (sensor_error_tally > 0) --sensor_error_tally;
		} 

		if (sensor_error != DS18B20_ERROR_OK) {
			++sensor_error_tally;
			if (sensor_error_tally > SENSOR_ERROR_RECOVERY_HYSTERESIS) sensor_error_tally = SENSOR_ERROR_RECOVERY_HYSTERESIS;
			++sensor_error_total;
		}

		_delay_ms(10);
		ds18b20convert(&PORTB, &DDRB, &PINB, (1 << 0), sensor_addr + (8 * i));
	}

	if (!valid_reads) return;

	temperature = (temperature_sum / (float)valid_reads) + temperature_correction;
}

void measure_humidity(void) {
	if (!humidity_sensor_initialized) return;

	uint16_t raw_read = ADC_read(0);
		
	float max_hum = (3.0 * 1023.0) / 5.0;
	humidity = ((float)raw_read / max_hum) + humidity_correction;
}

void switch_heater(uint8_t value) {
	if (heater_active == value) return;

	if (value) {
		PORTD |= 1 << PD4;
	} else {
		PORTD &= ~(1 << PD4);
		timer16_stop();
	}
}

void set_thermostat_enabled(uint8_t value) {
	if (value == OFF) {
		switch_heater(OFF);
		cooldown_active = OFF;
	}

	thermostat_enabled = !!value;
	eeprom_update_byte((uint8_t*)MEM_ENABLE, thermostat_enabled);
}

void set_target_temperature(float value) {
	target_temperature = value;
	eeprom_update_float((float*)MEM_TARGET_TEMPERATURE, target_temperature);
}

void set_temperature_correction(float value) {
	temperature_correction = value;
	eeprom_update_float((float*)MEM_TEMPERATURE_CORRECTION, temperature_correction);
}

void set_threshold_high(float value) {
	if (value < MIN_THRESHOLD) value = MIN_THRESHOLD;

	threshold_high = value;
	eeprom_update_float((float*)MEM_THRESHOLD_HIGH, threshold_high);
}

void set_threshold_low(float value) {
	if (value < MIN_THRESHOLD) value = MIN_THRESHOLD;

	threshold_low = value;
	eeprom_update_float((float*)MEM_THRESHOLD_LOW, threshold_low);
}

void set_humidity_correction(float value) {
	humidity_correction = value;
	eeprom_update_float((float*)MEM_HUMIDITY_CORRECTION, humidity_correction);
}

void set_max_heat_time(uint16_t value) {
	max_heat_time = value;
	eeprom_update_word((uint16_t*)MEM_MAX_HEAT_TIME, max_heat_time);
}

void set_min_cooldown_time(uint16_t value) {
	min_cooldown_time = value;
	eeprom_update_word((uint16_t*)MEM_MIN_COOLDOWN_TIME, min_cooldown_time);
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


void thermostat_init(void) {
	sensor_count = 0;
	sensor_error_tally = 0;
	cooldown_active = 0;

	sensor_error_total = 0;
	heater_triggered_count = 0;
	cooldown_triggered_count = 0;

	temperature = 420.0;

	thermostat_enabled = eeprom_read_byte((uint8_t*)MEM_ENABLE);
	target_temperature = eeprom_read_float((float*)MEM_TARGET_TEMPERATURE);
	temperature_correction = eeprom_read_float((float*)MEM_TEMPERATURE_CORRECTION);
	threshold_high = eeprom_read_float((float*)MEM_THRESHOLD_HIGH);
	threshold_low = eeprom_read_float((float*)MEM_THRESHOLD_LOW);
	humidity_correction = eeprom_read_float((float*)MEM_HUMIDITY_CORRECTION);
	max_heat_time = eeprom_read_word((uint16_t*)MEM_MAX_HEAT_TIME);
	min_cooldown_time = eeprom_read_word((uint16_t*)MEM_MIN_COOLDOWN_TIME);

	humidity = -69.0;
	humidity_sensor_initialized = 0;
	humidity_sensor_count = eeprom_read_byte((uint8_t*)THERMOSTAT_EEPROM_ADDR_HUMIDITY_SENSOR_COUNT);

	if (humidity_sensor_count) {
		ADC_init(0);
		humidity_sensor_initialized = 1;
		_delay_ms(10);
		measure_humidity();
	}

	// Heater relay
	DDRD |= 1 << PD4;
	PORTD &= ~(1 << PD4);

	ds18b20_init();
	_delay_ms(10);
	measure_temperature();
}

void system_error_lock(void) {
	switch_heater(OFF);
	nano_onboard_led_blink(-1, 1000);
}

void thermostat_control(void) {
	if (!sensor_count) ds18b20_init();

	measure_temperature();
	measure_humidity();

	if ((sensor_error_tally > SENSOR_ERROR_COUNT_MAX) ||
	  (heater_active && cooldown_active)) {
		system_error_lock();
	}

	if (!thermostat_enabled) return;

	if (heater_active) {
		if (timer16_flag) {
			switch_heater(OFF);
			cooldown_active = ON;
			timer16_init(min_cooldown_time);
			timer16_start();
		}

		if (temperature > (target_temperature + threshold_high)) {
			switch_heater(OFF);
		}

	} else if (cooldown_active) {
		if (timer16_flag) {
			cooldown_active = OFF;
			timer16_stop();
		}

		return;

	} else {
		if (temperature < (target_temperature - threshold_low)) {
			timer16_init(max_heat_time);
			timer16_start();
			switch_heater(ON);
		}
	}
}

uint8_t thermostat_state(void) {
	if (!thermostat_enabled) return 0;
	if (heater_active) return 2;
	if (cooldown_active) return 3;
	return 1;
}
