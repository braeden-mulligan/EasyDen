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

struct sh_device_metadata metadata;

char server_message[SERVER_MSG_SIZE_MAX];

inline void outlet_init(void) {
//TODO restore from storage
	DDRD |= (1 << PD4);
	DDRD |= (1 << PD5);
	DDRD |= (1 << PD6);
	DDRD |= (1 << PD7);
}

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
}

void handle_server_message(void) {
	char send_buf[SERVER_MSG_SIZE_MAX];
	struct sh_packet msg_packet;

	sh_parse_packet(&msg_packet, server_message);

	switch (msg_packet.cmd) {
	case CMD_GET:
		// check_and_handle_common_registers() else {
		msg_packet.cmd = CMD_RSP;
		if (msg_packet.reg == POWERSOCKET_REG_STATE) msg_packet.val = outlet_get();
		break;

	case CMD_SET:
		// check_and_handle_common_registers() else {
		msg_packet.cmd = CMD_RSP;
		if (msg_packet.reg == POWERSOCKET_REG_STATE) outlet_set(msg_packet.val);
		break;

	case CMD_IDY:
		msg_packet.cmd = CMD_IDY;
		msg_packet.reg = metadata.type;
		msg_packet.val = metadata.id;
		break;

	default:
		msg_packet.cmd = CMD_RSP;
		msg_packet.reg = SMARTHOME_REG_NULL;
		break;
	}

	sh_build_packet(&msg_packet, send_buf); 
//TODO: some error handling.
	if (wifi_send(send_buf) != ARDUINO_APP_SUCCESS) { };
}

void app_loop(void) {
/*
	blink_led(4, 1000);
	if (wifi_send(buf) != ARDUINO_APP_SUCCESS) start buffering messages
*/
}

int main(void) {
	load_metadata(&metadata);

	outlet_init();

	struct wifi_app_config app_conf = wifi_app_config_create();

	app_conf.wifi_startup_timeout = 10;
	app_conf.connection_interval = 30;
	app_conf.application_interval = 60;
	app_conf.server_buf_size = SERVER_MSG_SIZE_MAX;
	app_conf.server_message_buf = server_message;
	app_conf.server_message_callback = handle_server_message;
	app_conf.app_main_callback = app_loop;
	
	wifi_app_init(&app_conf);

	wifi_app_start();

	// If here is reached error occurred
	blink_led(-1, 1000);
	
	return 0;
}
