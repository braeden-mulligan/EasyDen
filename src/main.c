#include "avr_ESP8266_link.h"
#include "avr_timer_util.h"
#include "avr_utilities.h"

#include <stdio.h>
#include <string.h>
#include <util/delay.h>

//TODO: define in project library
#define ever ;;
#define SERVER_BUF_SIZE 32
#define WIFI_STARTUP_TIMEOUT 5
#define CMD_TIMEOUT_DEFAULT 5000

#ifndef WIFI_SSID 
	#error No wifi ssid defined.
#endif

#ifndef WIFI_PASS
	#error No wifi password defined.
#endif

#ifndef SOCKET_ADDR
	#error No socket address defined.
#endif

#ifndef SOCKET_PORT
	#error No socket port defined.
#endif

char server_buf[SERVER_BUF_SIZE];

struct ESP8266_network_parameters esp_params;

char* wifi_ssid = WIFI_SSID;
char* wifi_pass = WIFI_PASS;

uint8_t try_command(uint8_t (* command_func)(struct ESP8266_network_parameters*, uint32_t), uint32_t timeout_ms, uint8_t retries) {
	uint8_t result = ESP8266_CMD_FAILURE; 

	for (uint8_t i = 0; i < retries; ++i) {
		if ((result = command_func(&esp_params, timeout_ms)) == ESP8266_CMD_SUCCESS) break;
	}

	return result;
}

uint8_t module_check(void) {
	if (esp_params.command_echo) try_command(ESP8266_echo_disable, CMD_TIMEOUT_DEFAULT, 3); 

	if (!esp_params.wifi_mode) try_command(ESP8266_wifi_mode_get, CMD_TIMEOUT_DEFAULT, 2);

	if (esp_params.wifi_mode != ESP8266_MODE_STATION) try_command(ESP8266_wifi_mode_set, CMD_TIMEOUT_DEFAULT, 2);

	ESP8266_status(&esp_params, CMD_TIMEOUT_DEFAULT);

	return 0;
}

// Allow time for WiFi module startup.
void module_startup_procedure(void) {
	timer16_init(WIFI_STARTUP_TIMEOUT);
	timer16_start();

	while (!timer16_flag) {
		if (ESP8266_poll(&esp_params, 100) != ESP8266_RECV_FALSE) esp_params.module_ready = 1;
	}

	timer16_stop();

// In case the ESP8266 sent "ready" before the arduino could catch it.
	if (!esp_params.module_ready) {
		if (try_command(ESP8266_ping, CMD_TIMEOUT_DEFAULT, 3) == ESP8266_CMD_SUCCESS) {
			esp_params.module_ready = 1;
			blink_led(4, 300);
		}
	}
}

int main(void) {
	ESP8266_link_init(&esp_params, server_buf, 32, 3);

	module_startup_procedure();

	uint16_t debug_count = 0;
	char debug_msg[32];

	timer16_init(10);
	timer16_start();

	for (ever) {
		if (ESP8266_poll(&esp_params, 100) == ESP8266_RECV_SERVER) blink_led(5, 250);
	
		if (timer16_flag) {
			module_check();

			if (!esp_params.lan_connection) {
				ESP8266_lan_connect(&esp_params, 15000, WIFI_SSID, WIFI_PASS);
			} else if (!esp_params.ip_obtained) {
				// disconnect from AP to try reconnect?
			} else if (!esp_params.tcp_connection) {
				ESP8266_socket_connect(&esp_params, 8000, SOCKET_ADDR, SOCKET_PORT);
			} else {
				sprintf(debug_msg, "Sameple message #%d\r\n", debug_count);
				ESP8266_socket_send(&esp_params, 3000, debug_msg, strlen(debug_msg));
				++debug_count;
			}

			timer16_reset();
		}
	}

	return 0;
}
