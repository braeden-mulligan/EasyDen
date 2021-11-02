#include "arduino_wifi_app.h"
#include "ESP8266_link.h"
#include "avr_timer_util.h"
#include "avr_utilities.h"

#include <stddef.h>
#include <string.h>

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

static struct ESP8266_network_parameters esp_params;
static struct wifi_app_config* config;

static void process_server_message(void) {
	if (server_message_available()) {
		if (config->server_message_callback != NULL) config->server_message_callback();
		server_message_dequeue();
	}
}

static uint8_t try_command(uint8_t (* command_func)(struct ESP8266_network_parameters*, uint32_t), uint32_t timeout_ms, uint8_t retries) {
	uint8_t result = ESP8266_CMD_FAILURE; 

	for (uint8_t i = 0; i < retries; ++i) {
		if ((result = command_func(&esp_params, timeout_ms)) == ESP8266_CMD_SUCCESS) break;
	}

	process_server_message();

	return result;
}

// Allow time for WiFi module startup.
static void module_startup_procedure(void) {
	timer8_deinit();
//TODO check for existing init? unlikely.
	timer8_init(config->wifi_startup_timeout * 1000, 1);
	timer8_start();

	while (!timer8_flag) {
		if (ESP8266_poll(&esp_params, 100) != ESP8266_RECV_FALSE) esp_params.module_ready = 1;
	}

	timer8_stop();
	timer8_deinit();

// In case the ESP8266 sent "ready" before the arduino could catch it.
	if (!esp_params.module_ready) {
		if (try_command(ESP8266_ping, config->command_timeout, config->command_retries) == ESP8266_CMD_SUCCESS) {
			esp_params.module_ready = 1;
		}
	}

	blink_led(5, 200);
}

static uint8_t module_check(void) {
	if (esp_params.command_echo) try_command(ESP8266_echo_disable, config->command_timeout, config->command_retries); 

	if (!esp_params.wifi_mode) try_command(ESP8266_wifi_mode_get, config->command_timeout, config->command_retries);

	if (esp_params.wifi_mode != ESP8266_MODE_STATION) try_command(ESP8266_wifi_mode_set, config->command_timeout, config->command_retries);

	ESP8266_status(&esp_params, config->command_timeout);

	process_server_message();

	return 0;
}

static uint8_t module_poll(void) {
	uint8_t result;
	if ((result = ESP8266_poll(&esp_params, 100))) {
#if defined (DEBUG_MODE)
		if (result == ESP8266_RECV_SERVER) {
			blink_led(5, 250);
		} else if (result == MODULE_NOTIFICATION) {
			blink_led(2, 250);
		}
#endif
	}

	process_server_message();

	return 0;
}


/*
	Start of public funcitons
*/

void app_error_check(uint8_t retval) {
	switch(retval) {
	case ARDUINO_APP_SUCCESS:
		return;
#if defined (DEGUB_MODE)
	case ARDUINO_APP_ERROR:
		blink_led(-1, 1000);
		break;
#else 
	case ARDUINO_APP_ERROR:
		blink_led(3, 1000);
		break;
#endif

#if defined (DEBUG_MODE)
	case ESP8266_CMD_SUCCESS:
		blink_led(5, 200);
		break;
	case ESP8266_CMD_TIMEOUT:
		blink_led(1, 1000);
		break;
	case ESP8266_CMD_FAILURE:
		blink_led(2, 1000);
		break;
	case ESP8266_RECV_BUFOVERFLOW:
		blink_led(3, 1000);
		break;
	case ESP8266_CMD_SENDREADY:
		blink_led(4, 1000);
		break;
	case ESP8266_ERROR_UNKNOWN:
		blink_led(5, 1000);
		break;
#endif
	default:
		blink_led(-1, 300);
		break;
	}
}

uint8_t wifi_send(char* message) {
	uint8_t result = ARDUINO_APP_ERROR;

	if (esp_params.tcp_connection) {
		result = ESP8266_socket_send(&esp_params, config->command_timeout, message);
	}

	if (result == ESP8266_CMD_SUCCESS) return ARDUINO_APP_SUCCESS;
#if defined (DEBUG_MODE)
	return result;
#endif
	return ARDUINO_APP_ERROR;
}

struct wifi_app_config wifi_app_config_create(void) {
	struct wifi_app_config config_default = {
		.wifi_startup_timeout = WIFI_STARTUP_TIMEOUT_DEFAULT,
		.application_interval = APPLICATION_INTERVAL_DEFAULT,
		.connection_interval = CONNECTION_INTERVAL_DEFAULT,
		.command_retries = CMD_RETRIES_DEFAULT,
		.command_timeout = CMD_TIMEOUT_DEFAULT,
		.server_latency_timeout = SERVER_LATENCY_TIMEOUT_DEFAULT,
		.server_buf_size = SERVER_BUF_SIZE_DEFAULT,
		.server_message_buf = NULL,
		.server_message_callback = NULL,
		.app_main_callback = NULL
	};

	return config_default;
}

static uint8_t wifi_app_initialized = 0;

static uint16_t wifi_conn_clock_s;
static uint16_t wifi_app_clock_s;

uint8_t wifi_app_init(struct wifi_app_config* wac) {
	config = wac;

	wifi_conn_clock_s = 0;
	wifi_app_clock_s = 0;

	if (!wifi_app_initialized) {
		if (timer8_init(1000, 1) == TIMER_INIT_ERROR) return ARDUINO_APP_ERROR;
		ESP8266_link_init(&esp_params, config->server_message_buf, config->server_buf_size, config->server_latency_timeout);
		wifi_app_initialized = 1;
	}

	return ARDUINO_APP_SUCCESS;
}

static void socket_check(void){
	if (!esp_params.lan_connection) {
		ESP8266_lan_connect(&esp_params, config->wifi_startup_timeout, WIFI_SSID, WIFI_PASS);

	} else if (!esp_params.ip_obtained) {
		// disconnect from AP to try reconnect?

	} else if (!esp_params.tcp_connection) {
		ESP8266_socket_connect(&esp_params, config->wifi_startup_timeout, SOCKET_ADDR, SOCKET_PORT);
		/*
		if (cmd_result != ESP8266_CMD_SUCCESS) {
			uint8_t ssid_match;
			cmd_result = ESP8266_ap_query(&esp_params, config->command_timeout, WIFI_SSID, &ssid_match);

			if (cmd_result == ESP8266_CMD_SUCCESS && !ssid_match) {
				ESP8266_lan_disconnect(&esp_params, config->command_timeout);
			}
		}
		*/
	}
}

void wifi_app_start(void) {
	module_startup_procedure();

	socket_check();

	timer8_init(1000, 1);
	timer8_start();

	for (;;) {
		if (timer8_flag) {
			wifi_conn_clock_s += timer8_flag;
			wifi_app_clock_s += timer8_flag;
			timer8_restart();
		}

		if (wifi_conn_clock_s >= config->connection_interval) {
			module_check();

			socket_check();
	
			wifi_conn_clock_s = 0;
		}

		if (wifi_app_clock_s >= config->application_interval) {
			if (config->app_main_callback != NULL) config->app_main_callback();
			wifi_app_clock_s = 0;
		}

		module_poll();
	}
}
