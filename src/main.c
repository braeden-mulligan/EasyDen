#include "avr_ESP8266_link.h"
#include "avr_timer_util.h"
#include "avr_utilities.h"
#include "util/delay.h"

//TODO: define in project library
#define SERVER_BUF_SIZE 32

char server_buf[SERVER_BUF_SIZE];

struct ESP8266_network_parameters esp_params;

void operation_halt(void) {
	blink_led(-1,500);
}

uint8_t try_command(uint8_t (* command_func)(struct ESP8266_network_parameters*, uint16_t), uint16_t timeout_ms, uint8_t retries) {
	uint8_t result = ESP8266_CMD_FAILURE; 

	for (uint8_t i = 0; i < retries; ++i) {
		if ((result = command_func(&esp_params, timeout_ms)) == ESP8266_CMD_SUCCESS) break;
	}

	return result;
}

// Allow time for WiFi module startup.
void module_startup_procedure(void) {
	timer16_init(5);
	timer16_start();

	while (!timer16_flag) {
		ESP8266_poll(&esp_params, 100);
	}

	timer16_stop();

	if (esp_params.module_ready < 1) {
		//if (ESP8266_ping(&esp_params, 500) == ESP8266_CMD_SUCCESS) {
		if (try_command(&ESP8266_ping, 500, 3) == ESP8266_CMD_SUCCESS) {
			esp_params.module_ready = 1;
		} else {
			//operation_halt();
		}
	}

	if (try_command(&ESP8266_echo_disable, 500, 3) == ESP8266_CMD_SUCCESS) {
		esp_params.command_echo = 0;
	} else {
		//operation_halt();
	}

	//TODO:
	//check multiplexing
	//check wifi mode
}

int main(void) {
	ESP8266_link_init(&esp_params, server_buf, 32, 3);

	module_startup_procedure();

	while (1) {
		ESP8266_poll(&esp_params, 100);

		if (esp_params.lan_connection == 1) {
			blink_led(5, 250);
		} else {
			ESP8266_status(&esp_params, 500);
		}

		_delay_ms(1000);
	}

	return 0;
}
