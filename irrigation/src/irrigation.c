#include "irrigation.h"

#include "avr_adc.h"
#include "avr_utilities.h"
#include "avr_timer_util.h"
#include "device_definition.h"
#include "nano_configs_eeprom_offsets.h"

#include <avr/eeprom.h>
#include <avr/io.h>
#include <util/delay.h>

#define MEM_ENABLE 512
#define MEM_TARGET_MOISTURE (MEM_ENABLE + sizeof(irrigation_enabled))
// ...
#define MEM_SENSOR_RECORDED_MAX (MEM_TARGET_MOISTURE + sizeof(target_moisture))
#define MEM_SENSOR_RECORDED_MIN (MEM_SENSOR_RECORDED_MAX + sizeof(sensor_recorded_max))

enum {
	OFF = 0,
	ON
};

void set_irrigation_enabled(uint8_t value) {
	irrigation_enabled = !!value;
}

/*
void auto_calibrate_mode(uint8_t setting) {
	auto_calibration = !!setting;
	
	if (auto_calibration) {
		for (uint8_t i = 0; i < sensor_count; ++i) {
			sensor_raw_min[i] = sensor_recorded_min[i];
			sensor_raw_max[i] = sensor_recorded_max[i];
		}
	}
}
*/

void read_moisture(void) {
	for (uint8_t i = 0; i < sensor_count; ++i) {
		sensor_raw[i] = ADC_read(i);

		// if auto-calibration mode:
		// 	if sensor_raw < sensor_recorded_min: sensor_raw_min = sensor_recorded_min
		// 	if sensor_raw > sensor_recorded_min: sensor_raw_max = sensor_recorded_max

		moisture[i] = 100.0 - (100.0 * (float)((int32_t)sensor_raw[i] - (int32_t)sensor_raw_min[i]) / (float)(sensor_raw_max[i] - sensor_raw_min[i]));
	}
}

void irrigation_init(void) {
	sensor_count = eeprom_read_byte((uint8_t*)IRRIGATION_EEPROM_ADDR_SENSOR_COUNT);
	irrigation_enabled = eeprom_read_byte((uint8_t*)MEM_ENABLE);

	for (uint8_t i = 0; i < sensor_count; ++i) {
		target_moisture[i] = eeprom_read_float((float*)(MEM_TARGET_MOISTURE + (sizeof(float) * i)));
		sensor_recorded_max[i] = eeprom_read_word((uint16_t*)(MEM_SENSOR_RECORDED_MAX + (sizeof(uint16_t) * i)));
		sensor_recorded_min[i] = eeprom_read_word((uint16_t*)(MEM_SENSOR_RECORDED_MIN + (sizeof(uint16_t) * i)));
	}

	// moiture_low[]
	// moisture_change_hysteresis_time
	// moisture_change_hysteresis_amount
	// ?? max_water_time
	// min_cooldown_time
	// moisture_low_delay[]
	sensor_raw_max[0] = 750;
	sensor_raw_min[0] = 250;	
	sensor_raw_max[1] = 750;
	sensor_raw_min[1] = 250;

	ADC_init(0x3F);

	// Pump relay
	DDRD |= 1 << PD4;
	PORTD &= ~(1 << PD4);

	// Selection valve relays
	DDRD |= 1 << PD5;
	DDRD |= 1 << PD6;
	PORTD &= ~(1 << PD5);
	PORTD &= ~(1 << PD6);

	read_moisture();
}

void system_error_lock(void) {
	nano_onboard_led_blink(-1, 1000);
}

void irrigation_control(void) {
	nano_onboard_led_blink(4, 300);

	read_moisture();
}

uint8_t irrigation_state(void) {
	return 0;
}
