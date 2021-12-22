#include "arduino_wifi_app.h"
#include "device_definition.h"
//#include "protocol.h"
//#include "project_utilities.h"
#include "avr_utilities.h"

#include <avr/eeprom.h>
#include <avr/io.h>
#include <stdio.h>
#include <string.h>
#include <util/delay.h>

#define OUTLET_0_STATE !!(PORTD & (1 << PD4))
#define OUTLET_1_STATE !!(PORTD & (1 << PD5))
#define OUTLET_2_STATE !!(PORTD & (1 << PD6))
#define OUTLET_3_STATE !!(PORTD & (1 << PD7))
#define OUTLET_4_STATE !!(PORTD & (1 << PB0))
#define OUTLET_5_STATE !!(PORTD & (1 << PB1))
#define OUTLET_6_STATE !!(PORTD & (1 << PB2))
#define OUTLET_7_STATE !!(PORTD & (1 << PB3))

#define EEPROM_ADDR_SOCKET_COUNT 256

#define EEPROM_ADDR_OUTLET_0_MEM 512
#define EEPROM_ADDR_OUTLET_1_MEM 513
#define EEPROM_ADDR_OUTLET_2_MEM 514
#define EEPROM_ADDR_OUTLET_3_MEM 515
#define EEPROM_ADDR_OUTLET_4_MEM 516
#define EEPROM_ADDR_OUTLET_5_MEM 517
#define EEPROM_ADDR_OUTLET_6_MEM 518
#define EEPROM_ADDR_OUTLET_7_MEM 519

uint8_t socket_count;

uint32_t outlet_get(void) {
	uint32_t status_mask = 0;
	status_mask |= (OUTLET_0_STATE) << 0;
	status_mask |= (OUTLET_1_STATE) << 1;
	status_mask |= (OUTLET_2_STATE) << 2;
	status_mask |= (OUTLET_3_STATE) << 3;
	status_mask |= (OUTLET_4_STATE) << 4;
	status_mask |= (OUTLET_5_STATE) << 5;
	status_mask |= (OUTLET_6_STATE) << 6;
	status_mask |= (OUTLET_7_STATE) << 7;
	return status_mask;
}

void outlet_set(uint32_t status_mask) {
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
	if (reg == POWEROUTLET_REG_STATE) return outlet_get();
	if (reg == POWEROUTLET_REG_SOCKET_COUNT) return socket_count;
	return 0;
}

uint32_t handle_server_set(uint16_t reg, uint32_t val) {
	if (reg == POWEROUTLET_REG_STATE) {
		outlet_set(val);
		return outlet_get();
	}
	return 0;
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

	socket_count = eeprom_read_byte((uint8_t*)EEPROM_ADDR_SOCKET_COUNT);

	uint8_t outlet0 = eeprom_read_byte((uint8_t*)EEPROM_ADDR_OUTLET_0_MEM);
	uint8_t outlet1 = eeprom_read_byte((uint8_t*)EEPROM_ADDR_OUTLET_1_MEM);
	uint8_t outlet2 = eeprom_read_byte((uint8_t*)EEPROM_ADDR_OUTLET_2_MEM);
	uint8_t outlet3 = eeprom_read_byte((uint8_t*)EEPROM_ADDR_OUTLET_3_MEM);
	uint8_t outlet4 = eeprom_read_byte((uint8_t*)EEPROM_ADDR_OUTLET_4_MEM);
	uint8_t outlet5 = eeprom_read_byte((uint8_t*)EEPROM_ADDR_OUTLET_5_MEM);
	uint8_t outlet6 = eeprom_read_byte((uint8_t*)EEPROM_ADDR_OUTLET_6_MEM);
	uint8_t outlet7 = eeprom_read_byte((uint8_t*)EEPROM_ADDR_OUTLET_7_MEM);

	uint32_t status_mask = 0x0000FF00;
	status_mask |= outlet0 | (outlet1 << 1) | (outlet2 << 2) | (outlet3 << 3);
	status_mask |= (outlet4 << 4) | (outlet5 << 5) | (outlet5 << 6) | (outlet6 << 7);
	outlet_set(status_mask);
}

int main(void) {
	outlet_init();

	struct wifi_app_config app_conf = wifi_app_config_create();

	app_conf.wifi_startup_timeout = 7;
	app_conf.connection_interval = 20;
	app_conf.server_message_get_callback = handle_server_get;
	app_conf.server_message_set_callback = handle_server_set;
	
	wifi_app_init(&app_conf);

	wifi_app_start();

	// If here is reached, error occurred
	blink_led(-1, 1000);
	
	return 0;
}
