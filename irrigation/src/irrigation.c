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
#define MEM_PLANT_ENABLE_MASK (MEM_ENABLE + sizeof(irrigation_enabled))
#define MEM_AUTO_CALIBRATION (MEM_PLANT_ENABLE_MASK + sizeof(plant_enable_mask))
#define MEM_TARGET_MOISTURE (MEM_AUTO_CALIBRATION + sizeof(auto_calibration))
#define MEM_MOISTURE_LOW (MEM_TARGET_MOISTURE + sizeof(target_moisture))
#define MEM_MOISTURE_LOW_DELAY (MEM_MOISTURE_LOW + sizeof(moisture_low))
#define MEM_MOISTURE_CHANGE_HYSTERESIS_TIME (MEM_MOISTURE_LOW_DELAY + sizeof(moisture_low_delay))
#define MEM_MOISTURE_CHANGE_HYSTERESIS_AMOUNT (MEM_MOISTURE_CHANGE_HYSTERESIS_TIME + sizeof(moisture_change_hysteresis_time))
#define MEM_SENSOR_RAW_MAX (MEM_MOISTURE_CHANGE_HYSTERESIS_AMOUNT + sizeof(moisture_change_hysteresis_amount))
#define MEM_SENSOR_RAW_MIN (MEM_SENSOR_RAW_MAX + sizeof(sensor_raw_max))
#define MEM_SENSOR_RECORDED_MAX (MEM_SENSOR_RAW_MIN + sizeof(sensor_raw_min))
#define MEM_SENSOR_RECORDED_MIN (MEM_SENSOR_RECORDED_MAX + sizeof(sensor_recorded_max))

#define PLANT_1_MASK 1
#define PLANT_2_MASK 2
#define PLANT_3_MASK 4

#define pump_active (!!(PORTD & (1 << PD4)))

enum {
	OFF = 0,
	ON
};

uint8_t plant_select;

void valve_switch(uint8_t select) {
	switch (select) {
	case 2:
		PORTD |= 1 << PD6;
	case 1:
		PORTD |= 1 << PD5;
		break;

	case 0:	
	default:
		PORTD &= ~(1 << PD5);
		PORTD &= ~(1 << PD6);
	}
}

void set_irrigation_enabled(uint8_t setting) {
	if (setting == OFF) {
		switch_pump(OFF);
		valve_switch(0);
	}

	irrigation_enabled = !!setting;
	eeprom_update_byte((uint8_t*)MEM_ENABLE, irrigation_enabled);
}

void set_sensor_raw_min(uint8_t sensor_select, uint16_t value) {
	sensor_raw_min[sensor_select] = value;
	eeprom_update_word
}

void set_sensor_raw_max(uint8_t sensor_select, uint16_t value) {
	sensor_raw_max[sensor_select] = value;
	eeprom_update_word
}

void auto_calibrate(void) {
	if (auto_calibration) {
		for (uint8_t i = 0; i < sensor_count; ++i) {
			set_sensor_raw_min(i, sensor_recorded_min[i]);
			set_sensor_raw_max(i, sensor_recorded_max[i]);
		}
	}
} 

void set_auto_calibration(uint8_t setting) {
	auto_calibration = !!setting;
	auto_calibrate();
}

void switch_pump(uint8_t setting) {
	if (setting) {
		PORTD |= 1 << PD4;
	} else {
		PORTD &= ~(1 << PD4);
	}
}

void read_moisture(void) {
	for (uint8_t i = 0; i < sensor_count; ++i) {
		_delay_ms(10);
		sensor_raw[i] = ADC_read(i);

		if (sensor_raw[i] < sensor_recorded_min[i]) {
			sensor_recorded_min[i] = sensor_raw[i];
			auto_calibrate();
		}

		if (sensor_raw[i] < sensor_recorded_min[i]) {
			sensor_recorded_min[i] = sensor_raw[i];
			auto_calibrate();
		}

		moisture[i] = 100.0 - (100.0 * (float)((int32_t)sensor_raw[i] - (int32_t)sensor_raw_min[i]) / (float)(sensor_raw_max[i] - sensor_raw_min[i]));
	}
}

void irrigation_init(void) {
	plant_select = 0;

	ADC_init(0x3F);

	// Pump relay
	DDRD |= 1 << PD4;
	PORTD &= ~(1 << PD4);

	// Selection valve relays
	DDRD |= 1 << PD5;
	DDRD |= 1 << PD6;
	valve_switch(plant_select);

	sensor_count = eeprom_read_byte((uint8_t*)IRRIGATION_EEPROM_ADDR_SENSOR_COUNT);
	irrigation_enabled = eeprom_read_byte((uint8_t*)MEM_ENABLE);
	plant_enable_mask = eeprom_read_byte((uint8_t*)MEM_PLANT_ENABLE_MASK);
	auto_calibration = eeprom_read_byte((uint8_t*)MEM_AUTO_CALIBRATION);
	moisture_change_hysteresis_time = eeprom_read_word((uint16_t*)MEM_MOISTURE_CHANGE_HYSTERESIS_TIME);
	moisture_change_hysteresis_amount = eeprom_read_word((uint16_t*)MEM_MOISTURE_CHANGE_HYSTERESIS_AMOUNT);

	for (uint8_t i = 0; i < sensor_count; ++i) {
		target_moisture[i] = eeprom_read_float((float*)(MEM_TARGET_MOISTURE + (sizeof(float) * i)));
		moisture_low[i] = eeprom_read_float((float*)(MEM_MOISTURE_LOW + (sizeof(float) * i)));
		moisture_low_delay[i] = eeprom_read_dword((uint32_t*)MEM_MOISTURE_LOW_DELAY);
		sensor_raw_max[i] = eeprom_read_word((uint16_t*)(MEM_SENSOR_RAW_MAX + (sizeof(uint16_t) * i)));
		sensor_raw_min[i] = eeprom_read_word((uint16_t*)(MEM_SENSOR_RAW_MIN + (sizeof(uint16_t) * i)));
		sensor_recorded_max[i] = eeprom_read_word((uint16_t*)(MEM_SENSOR_RECORDED_MAX + (sizeof(uint16_t) * i)));
		sensor_recorded_min[i] = eeprom_read_word((uint16_t*)(MEM_SENSOR_RECORDED_MIN + (sizeof(uint16_t) * i)));
	}
	
	read_moisture();
}

void system_error_lock(void) {
	nano_onboard_led_blink(-1, 1000);
}

void irrigation_control(void) {
	read_moisture();

	if (!irrigation_enabled) return;

/*
	if auto_calibration
		do stuff
		return;
*/

/*
	if (pump_active) {
		do checks for current_plant
			- moisture target reached
			- hysteresis limits
			- water time/amount limit
	} else {
		for (uint8_t i; i < SENSOR_COUNT_MAX; ++i) {
			if (plant_enable_mask & (1 << i) && moisture[i] < moisture_low[i] && timer > moisture_low_delay[i]) {
				plant_select = i;
				start pump, set pump start time, set raw sensor start value;
				return;
			} 
		}
	}
*/
}

// TODO handle bad reads?
