#include "arduino_wifi_app.h"
#include "avr_utilities.h"

#include <stdio.h>
#include <string.h>
#include <util/delay.h>

#define SERVER_MSG_SIZE_MAX 32

char server_message[SERVER_MSG_SIZE_MAX];

void handle_server_message(void) {
	blink_led(5, 250);
}

uint16_t debug_counter = 0;

void app_loop(void) {
	char msg[16];
	sprintf(msg, "dbg: %u", debug_counter);
	wifi_send(msg);
	debug_counter += 1;
}

int main(void) {

	struct wifi_app_config app_conf = wifi_app_config_create();

	app_conf.wifi_startup_timeout = 10;
	app_conf.application_interval = 5;
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
