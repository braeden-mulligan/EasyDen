#include "arduino_wifi_framework.h"
#include "device_definition.h"
#include "avr_utilities.h"
#include "nano_configs_eeprom_offsets.h"

#include <avr/eeprom.h>
#include <avr/io.h>
#include <stdio.h>
#include <string.h>
#include <util/delay.h>

#define OUTLET_0_STATE !!(PORTD & (1 << PD4))
#define OUTLET_1_STATE !!(PORTD & (1 << PD5))
#define OUTLET_2_STATE !!(PORTD & (1 << PD6))
#define OUTLET_3_STATE !!(PORTD & (1 << PD7))
#define OUTLET_4_STATE !!(PORTB & (1 << PB0))
#define OUTLET_5_STATE !!(PORTB & (1 << PB1))
#define OUTLET_6_STATE !!(PORTB & (1 << PB2))
#define OUTLET_7_STATE !!(PORTB & (1 << PB3))

#define EEPROM_ADDR_OUTLET_0_MEM 512
#define EEPROM_ADDR_OUTLET_1_MEM 513
#define EEPROM_ADDR_OUTLET_2_MEM 514
#define EEPROM_ADDR_OUTLET_3_MEM 515
#define EEPROM_ADDR_OUTLET_4_MEM 516
#define EEPROM_ADDR_OUTLET_5_MEM 517
#define EEPROM_ADDR_OUTLET_6_MEM 518
#define EEPROM_ADDR_OUTLET_7_MEM 519

#define EEPROM_ADDR_ENABLED 520

uint8_t poweroutlet_enabled;
uint8_t socket_count;
uint8_t values_inverted;

struct wifi_framework_config app_conf;
struct wifi_framework_config tmp_conf;

uint8_t blink_trigger;

void set_conf_fast_period(void) {
	tmp_conf = app_conf;
	tmp_conf.application_interval = 1;
	wifi_framework_init(tmp_conf);
}

void restore_app_conf(void) {
	wifi_framework_init(app_conf);
}

uint32_t outlet_state_get(void) {
	uint32_t status_mask = 0;
	status_mask |= (OUTLET_0_STATE) << 0;
	status_mask |= (OUTLET_1_STATE) << 1;
	status_mask |= (OUTLET_2_STATE) << 2;
	status_mask |= (OUTLET_3_STATE) << 3;
	status_mask |= (OUTLET_4_STATE) << 4;
	status_mask |= (OUTLET_5_STATE) << 5;
	status_mask |= (OUTLET_6_STATE) << 6;
	status_mask |= (OUTLET_7_STATE) << 7;

	return values_inverted ? ~(0xFFFFFF00 | status_mask) : status_mask; 
}

void outlet_state_set(uint32_t status_mask) {
	if (!poweroutlet_enabled) return;

	if (values_inverted) status_mask = (0x0000FF00 & status_mask) | (0x000000FF & ~status_mask);

	if (status_mask & (1 << 8)) {
		if (status_mask & (1 << 0)) {
			PORTD |= (1 << PD4); 
		} else {	
			PORTD &= ~(1 << PD4);
		}
	}
	if (status_mask & (1 << 9)) {
		if (status_mask & (1 << 1)) {
			PORTD |= (1 << PD5); 
		} else {
			PORTD &= ~(1 << PD5);
		}
	}
	if (status_mask & (1 << 10)) {
		if (status_mask & (1 << 2)) {
			PORTD |= (1 << PD6); 
		} else {
			PORTD &= ~(1 << PD6);
		}
	}
	if (status_mask & (1 << 11)) {
		if (status_mask & (1 << 3)) {
			PORTD |= (1 << PD7); 
		} else {
			PORTD &= ~(1 << PD7);
		}
	}

	if (status_mask & (1 << 12)) {
		if (status_mask & (1 << 4)) {
			PORTB |= (1 << PB0); 
		} else {
			PORTB &= ~(1 << PB0);
		}
	}
	if (status_mask & (1 << 13)) {
		if (status_mask & (1 << 5)) {
			PORTB |= (1 << PB1); 
		} else {
			PORTB &= ~(1 << PB1);
		}
	}
	if (status_mask & (1 << 14)) {
		if (status_mask & (1 << 6)) {
			PORTB |= (1 << PB2); 
		} else {
			PORTB &= ~(1 << PB2);
		}
	}
	if (status_mask & (1 << 15)) {
		if (status_mask & (1 << 7)) {
			PORTB |= (1 << PB3); 
		} else {
			PORTB &= ~(1 << PB1);
		}
	}

	eeprom_update_byte((uint8_t*)EEPROM_ADDR_OUTLET_0_MEM, OUTLET_0_STATE);
	eeprom_update_byte((uint8_t*)EEPROM_ADDR_OUTLET_1_MEM, OUTLET_1_STATE);
	eeprom_update_byte((uint8_t*)EEPROM_ADDR_OUTLET_2_MEM, OUTLET_2_STATE);
	eeprom_update_byte((uint8_t*)EEPROM_ADDR_OUTLET_3_MEM, OUTLET_3_STATE);
	eeprom_update_byte((uint8_t*)EEPROM_ADDR_OUTLET_4_MEM, OUTLET_4_STATE);
	eeprom_update_byte((uint8_t*)EEPROM_ADDR_OUTLET_5_MEM, OUTLET_5_STATE);
	eeprom_update_byte((uint8_t*)EEPROM_ADDR_OUTLET_6_MEM, OUTLET_6_STATE);
	eeprom_update_byte((uint8_t*)EEPROM_ADDR_OUTLET_7_MEM, OUTLET_7_STATE);
}

uint32_t handle_server_get(uint16_t reg) {
	if (reg == GENERIC_ATTR_ENABLE) return poweroutlet_enabled;
	if (reg == POWEROUTLET_ATTR_STATE) return outlet_state_get();
	if (reg == POWEROUTLET_ATTR_SOCKET_COUNT) return socket_count;
	return 0;
}

uint32_t handle_server_set(uint16_t reg, uint32_t val) {
	if (reg == GENERIC_ATTR_ENABLE) {
		poweroutlet_enabled = !!val;
		eeprom_update_byte((uint8_t*)EEPROM_ADDR_ENABLED, poweroutlet_enabled);

		if (!poweroutlet_enabled) outlet_state_set(0x0000FF00);

		return poweroutlet_enabled;
	}

	if (reg == GENERIC_ATTR_BLINK) {
		set_conf_fast_period();
		blink_trigger = 1;
	}

	if (reg == POWEROUTLET_ATTR_STATE) {
		outlet_state_set(val);
		return outlet_state_get();
	}

	return 0;
}

void blink_identify(void) {
	if (blink_trigger) {
		blink_trigger = 0;

		uint32_t saved_outlet_state = outlet_state_get();

		for (uint8_t i = 0; i < 3; ++i) {
			outlet_state_set(0x0000FFFF);
			_delay_ms(750);
			outlet_state_set(0x0000FF00);
			_delay_ms(750);
		}

		outlet_state_set(0x0000FF00 | saved_outlet_state);

		restore_app_conf();
	}
}

void outlet_init(void) {
	DDRD |= (1 << PD4);
	DDRD |= (1 << PD5);
	DDRD |= (1 << PD6);
	DDRD |= (1 << PD7);

	DDRB |= (1 << PB0);
	DDRB |= (1 << PB1);
	DDRB |= (1 << PB2);
	DDRB |= (1 << PB3);

	socket_count = eeprom_read_byte((uint8_t*)POWEROUTLET_EEPROM_ADDR_SOCKET_COUNT);
	values_inverted = eeprom_read_byte((uint8_t*)POWEROUTLET_EEPROM_ADDR_VALUES_INVERTED);
	poweroutlet_enabled = eeprom_read_byte((uint8_t*)EEPROM_ADDR_ENABLED);

	uint8_t outlet0 = eeprom_read_byte((uint8_t*)EEPROM_ADDR_OUTLET_0_MEM);
	uint8_t outlet1 = eeprom_read_byte((uint8_t*)EEPROM_ADDR_OUTLET_1_MEM);
	uint8_t outlet2 = eeprom_read_byte((uint8_t*)EEPROM_ADDR_OUTLET_2_MEM);
	uint8_t outlet3 = eeprom_read_byte((uint8_t*)EEPROM_ADDR_OUTLET_3_MEM);
	uint8_t outlet4 = eeprom_read_byte((uint8_t*)EEPROM_ADDR_OUTLET_4_MEM);
	uint8_t outlet5 = eeprom_read_byte((uint8_t*)EEPROM_ADDR_OUTLET_5_MEM);
	uint8_t outlet6 = eeprom_read_byte((uint8_t*)EEPROM_ADDR_OUTLET_6_MEM);
	uint8_t outlet7 = eeprom_read_byte((uint8_t*)EEPROM_ADDR_OUTLET_7_MEM);

	uint32_t status_mask = 0x0000FF00;
	status_mask |= outlet0 << 0;
	status_mask |= outlet1 << 1;
	status_mask |= outlet2 << 2;
	status_mask |= outlet3 << 3;
	status_mask |= outlet4 << 4;
	status_mask |= outlet5 << 5;
	status_mask |= outlet6 << 6;
	status_mask |= outlet7 << 7;
	
	if (values_inverted) status_mask = (0x0000FF00 | ~status_mask);

	outlet_state_set(status_mask);
}

int main(void) {
	blink_trigger = 0;
	outlet_init();

	app_conf = wifi_framework_config_create();

	app_conf.wifi_startup_timeout = 7;
	app_conf.connection_interval = 20;
	app_conf.server_message_get_callback = handle_server_get;
	app_conf.server_message_set_callback = handle_server_set;
	app_conf.app_main_callback = blink_identify;
	
	wifi_framework_init(app_conf);

	wifi_framework_start();

	// If here is reached, error occurred
	nano_onboard_led_blink(-1, 1000);
	
	return 0;
}
