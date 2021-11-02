#include "arduino_wifi_app.h"
#include "device_definition.h"
#include "protocol.h"
#include "project_utilities.h"
#include "avr_utilities.h"

#include <avr/eeprom.h>
#include <avr/io.h>
#include <stdio.h>
#include <string.h>
#include <util/delay.h>

#define SERVER_MSG_SIZE_MAX 32

#define OUTLET_0_STATE !!(PORTD & (1 << PD4))
#define OUTLET_1_STATE !!(PORTD & (1 << PD5))
#define OUTLET_2_STATE !!(PORTD & (1 << PD6))
#define OUTLET_3_STATE !!(PORTD & (1 << PD7))

#define OUTLET_0_MEM 256
#define OUTLET_1_MEM 257
#define OUTLET_2_MEM 258
#define OUTLET_3_MEM 259

struct sh_device_metadata metadata;

char server_message[SERVER_MSG_SIZE_MAX];

int32_t outlet_get(void) {
	int32_t status_mask = 0;
	status_mask |= (OUTLET_0_STATE) << 0;
	status_mask |= (OUTLET_1_STATE) << 1;
	status_mask |= (OUTLET_2_STATE) << 2;
	status_mask |= (OUTLET_3_STATE) << 3;
	return status_mask;
}

void outlet_set(int32_t status_mask) {
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

	eeprom_update_byte((uint8_t*)OUTLET_0_MEM, OUTLET_0_STATE);
	eeprom_update_byte((uint8_t*)OUTLET_1_MEM, OUTLET_1_STATE);
	eeprom_update_byte((uint8_t*)OUTLET_2_MEM, OUTLET_2_STATE);
	eeprom_update_byte((uint8_t*)OUTLET_3_MEM, OUTLET_3_STATE);
}

void handle_server_message(void) {
	char send_buf[SERVER_MSG_SIZE_MAX];
	struct sh_packet msg_packet;

	if (sh_parse_packet(&msg_packet, server_message) != SH_PROTOCOL_SUCCESS) return;

	switch (msg_packet.cmd) {
	case CMD_GET:
		//TODO: check_and_handle_common_registers() else { application specific
		msg_packet.cmd = CMD_RSP;
		if (msg_packet.reg == POWEROUTLET_REG_STATE) msg_packet.val = outlet_get();
		break;

	case CMD_SET:
		//TODO: check_and_handle_common_registers() else { application specific
		msg_packet.cmd = CMD_RSP;
		if (msg_packet.reg == POWEROUTLET_REG_STATE) outlet_set(msg_packet.val);
		break;

	case CMD_IDY:
		msg_packet.cmd = CMD_IDY;
		msg_packet.reg = metadata.type;
		msg_packet.val = metadata.id;
		break;

	default:
		msg_packet.cmd = CMD_RSP;
		msg_packet.reg = GENERIC_REG_NULL;
		break;
	}

	if (sh_build_packet(&msg_packet, send_buf) != SH_PROTOCOL_SUCCESS) return;
	if (wifi_send(send_buf) != ARDUINO_APP_SUCCESS) { };
}

void outlet_init(void) {
	DDRD |= (1 << PD4);
	DDRD |= (1 << PD5);
	DDRD |= (1 << PD6);
	DDRD |= (1 << PD7);

	uint8_t outlet0 = eeprom_read_byte((uint8_t*)OUTLET_0_MEM);
	uint8_t outlet1 = eeprom_read_byte((uint8_t*)OUTLET_1_MEM);
	uint8_t outlet2 = eeprom_read_byte((uint8_t*)OUTLET_2_MEM);
	uint8_t outlet3 = eeprom_read_byte((uint8_t*)OUTLET_3_MEM);

	int32_t status_mask = 0x0000FF00;
	status_mask |= outlet0 | (outlet1 << 1) | (outlet2 << 2) | (outlet3 << 3);
	outlet_set(status_mask);
}

int main(void) {
	load_metadata(&metadata);

	outlet_init();

	struct wifi_app_config app_conf = wifi_app_config_create();

	app_conf.wifi_startup_timeout = 7;
	app_conf.connection_interval = 20;
	app_conf.server_buf_size = SERVER_MSG_SIZE_MAX;
	app_conf.server_message_buf = server_message;
	app_conf.server_message_callback = handle_server_message;
	
	wifi_app_init(&app_conf);

	wifi_app_start();

	// If here is reached error occurred
	blink_led(-1, 1000);
	
	return 0;
}
