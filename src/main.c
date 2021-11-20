#include "arduino_wifi_app.h"
#include "device_definition.h"
#include "protocol.h"
#include "project_utilities.h"
#include "avr_utilities.h"

#include "ds18b20/ds18b20.h"
#include "ds18b20/romsearch.h"

#include <avr/eeprom.h>
#include <avr/io.h>
#include <stdio.h>
#include <string.h>
#include <util/delay.h>

#define SERVER_MSG_SIZE_MAX 32

struct sh_device_metadata metadata;

char server_message[SERVER_MSG_SIZE_MAX];

int16_t temp0;
int16_t temp1;

uint8_t sensor_count;
uint8_t sensor_addr[32];

void sensor_init(void) {
	ds18b20search(&PORTB, &DDRB, &PINB, (1 << 0), &sensor_count, sensor_addr, sizeof(sensor_addr));
}

void measure_temperature(void) {
	ds18b20convert(&PORTB, &DDRB, &PINB, (1 << 0), sensor_addr);
	_delay_ms(10);
	ds18b20convert(&PORTB, &DDRB, &PINB, (1 << 0), sensor_addr + 8);

	_delay_ms(1000);

	ds18b20read(&PORTB, &DDRB, &PINB, (1 << 0), sensor_addr, &temp0);
	_delay_ms(10);
	ds18b20read(&PORTB, &DDRB, &PINB, (1 << 0), sensor_addr + 8, &temp1);
}

//TODO: Debug only
uint32_t temp_get() {
	measure_temperature();
	return (uint32_t)temp1 << 16 | (uint32_t)temp0;
}

void handle_server_message(void) {
	char send_buf[SERVER_MSG_SIZE_MAX];
	struct sh_packet msg_packet;

	if (sh_parse_packet(&msg_packet, server_message) != SH_PROTOCOL_SUCCESS) return;

	switch (msg_packet.cmd) {
	case CMD_GET:
		//TODO: check_and_handle_common_registers() else { application specific
		msg_packet.cmd = CMD_RSP;
		if (msg_packet.reg == POWEROUTLET_REG_STATE) msg_packet.val = temp_get();
		break;

	case CMD_SET:
		//TODO: check_and_handle_common_registers() else { application specific
		msg_packet.cmd = CMD_RSP;
		//if (msg_packet.reg == POWEROUTLET_REG_STATE) outlet_set(msg_packet.val);
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

int main(void) {
	load_metadata(&metadata);

	struct wifi_app_config app_conf = wifi_app_config_create();

	sensor_init();

	app_conf.wifi_startup_timeout = 7;
	app_conf.connection_interval = 20;
	app_conf.application_interval = 120;
	app_conf.server_buf_size = SERVER_MSG_SIZE_MAX;
	app_conf.server_message_buf = server_message;
	app_conf.server_message_callback = handle_server_message;
	app_conf.app_main_callback = measure_temperature;
	
	wifi_app_init(&app_conf);

	wifi_app_start();

	// If here is reached error occurred
	blink_led(-1, 1000);
	
	return 0;
}
