#include "arduino_wifi_app.h"
#include "avr_utilities.h"

#include <avr/io.h>
#include <stdio.h>
#include <string.h>
#include <util/delay.h>

#define SERVER_MSG_SIZE_MAX 32

char server_message[SERVER_MSG_SIZE_MAX];

uint16_t message_counter = 0;

void handle_server_message(void) {
	blink_led(3, 300);

	++message_counter;

	if (!strcmp(server_message, "on")) {
		PORTB |= (1 << PB5);
		wifi_send("LED switched ON");

	} else if (!strcmp(server_message, "off")) {
		PORTB &= ~(1 << PB5);
		wifi_send("LED switched OFF");
	}
}

void app_loop(void) {
	char buf[32];
	sprintf(buf, "%u messages since boot", message_counter);
	wifi_send(buf);
}

int main(void) {
	DDRB |= (1 << PB5);

	struct wifi_app_config app_conf = wifi_app_config_create();

	app_conf.wifi_startup_timeout = 10;
	app_conf.application_interval = 30;
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
