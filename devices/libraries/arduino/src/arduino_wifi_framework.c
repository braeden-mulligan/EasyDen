#include "arduino_wifi_framework.h"
#include "ESP8266_link.h"
#include "avr_timer_util.h"
#include "avr_utilities.h"
#include "device_definition.h"
#include "protocol.h"
#include "project_utilities.h"

#include <stddef.h>
#include <string.h>

#ifndef WIFI_SSID 
	#error No wifi ssid defined.
#else
	char* wifi_ssid = WIFI_SSID;
#endif

#ifndef WIFI_PASS
	#error No wifi password defined.
#else
	char* wifi_pass = WIFI_PASS;
#endif

#ifndef SOCKET_ADDR
	#error No socket address defined.
#else
	char* socket_addr = SOCKET_ADDR;
#endif

#ifndef SOCKET_PORT
	#error No socket port defined.
#else
	char* socket_port = SOCKET_PORT;
#endif

static struct sh_device_metadata metadata;

static struct ESP8266_network_parameters esp_params;

static struct wifi_framework_config config;

static char server_message_buf[SERVER_MSG_SIZE_MAX];

static void error_check(uint8_t cmd_result) {
	switch (cmd_result) {
	case ESP8266_CMD_SUCCESS: return;
	case ESP8266_CMD_FAILURE:
	case ESP8266_CMD_TIMEOUT:
	case ESP8266_CMD_ERROR:
	default:
		for (uint32_t i = 0; i < config.command_timeout; i += 100) {
			ESP8266_poll(&esp_params, 100);
		}

		//nano_onboard_led_blink(5, 500);

		break;
	}
}

static void process_server_message(void) {
	if (server_message_available()) {
		char send_buf[SERVER_MSG_SIZE_MAX];
		struct sh_packet msg_packet;

		if (sh_parse_packet(&msg_packet, server_message_buf) != SH_PROTOCOL_SUCCESS) return;

		switch (msg_packet.cmd) {
		case CMD_GET:
			msg_packet.cmd = CMD_RSP;
			if (config.server_message_get_callback != NULL) {
				msg_packet.val = config.server_message_get_callback(msg_packet.reg);
			}
			break;

		case CMD_SET:
			msg_packet.cmd = CMD_RSP;
			if (config.server_message_set_callback != NULL) {
				msg_packet.val = config.server_message_set_callback(msg_packet.reg, msg_packet.val);
			}
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
		if (wifi_send(send_buf) != ARDUINO_WIFI_SUCCESS) {
			//config.server_message_error_callback();
		}

		server_message_dequeue();
	}
}

static uint8_t try_command(uint8_t (* command_func)(struct ESP8266_network_parameters*, uint32_t), uint32_t timeout_ms, uint8_t retries) {
	uint8_t result = ESP8266_CMD_FAILURE; 

	for (uint8_t i = 0; i < retries; ++i) {
		if ((result = command_func(&esp_params, timeout_ms)) == ESP8266_CMD_SUCCESS) break;
	}
	error_check(result);

	process_server_message();

	return result;
}

// Allow time for WiFi module startup.
static void module_startup_procedure(void) {
	timer8_init(config.wifi_startup_timeout * 1000, 1);
	timer8_start();

	while (!timer8_flag) {
		if (ESP8266_poll(&esp_params, 100) != ESP8266_RECV_FALSE) esp_params.module_ready = 1;
	}

	timer8_stop();

// In case the ESP8266 sent "ready" before the arduino could catch it.
	if (!esp_params.module_ready) {
		if (try_command(ESP8266_ping, config.command_timeout, config.command_retries) == ESP8266_CMD_SUCCESS) {
			esp_params.module_ready = 1;
		}
	}
}

static uint8_t ssid_match = 0;

static void module_check(void) {
	uint8_t cmd_result;

	if (esp_params.command_echo) try_command(ESP8266_echo_disable, config.command_timeout, config.command_retries); 

	if (!esp_params.wifi_mode) try_command(ESP8266_wifi_mode_get, config.command_timeout, config.command_retries);

	if (esp_params.wifi_mode != ESP8266_MODE_STATION) {
		if (try_command(ESP8266_wifi_mode_set, config.command_timeout, config.command_retries) != ESP8266_CMD_SUCCESS) return;
	}

	for (uint8_t i = 0; (i < 3) && (!ssid_match); ++i) {
		cmd_result = ESP8266_ap_query(&esp_params, config.command_timeout, wifi_ssid, &ssid_match);
		error_check(cmd_result);

		if (cmd_result == ESP8266_CMD_SUCCESS && !ssid_match) {
			error_check(ESP8266_lan_connect(&esp_params, config.wifi_startup_timeout * 1000, wifi_ssid, wifi_pass)); 
		}
	}

	try_command(ESP8266_status, config.command_timeout, config.command_retries);

	if (!esp_params.lan_connection) {
		return;

	} else if (!esp_params.ip_obtained) {
		return;

	} else if (!esp_params.tcp_connection) {
		error_check(ESP8266_socket_connect(&esp_params, config.wifi_startup_timeout * 1000, socket_addr, socket_port));
	} 

	process_server_message();
}

/*
	Start of public funcitons
*/
uint8_t wifi_send(char* message) {
	uint8_t result = ESP8266_CMD_SUCCESS;

	if (esp_params.tcp_connection) {
		result = ESP8266_socket_send(&esp_params, config.command_timeout, message);
	}

	if (result == ESP8266_CMD_SUCCESS) return ARDUINO_WIFI_SUCCESS;

	error_check(result);

	return ARDUINO_WIFI_ERROR;
}

struct wifi_framework_config wifi_framework_config_create(void) {
	struct wifi_framework_config config_default = {
		.wifi_startup_timeout = WIFI_STARTUP_TIMEOUT_DEFAULT,
		.application_interval = APPLICATION_INTERVAL_DEFAULT,
		.connection_interval = CONNECTION_INTERVAL_DEFAULT,
		.command_retries = CMD_RETRIES_DEFAULT,
		.command_timeout = CMD_TIMEOUT_DEFAULT,
		.server_latency_timeout = SERVER_LATENCY_TIMEOUT_DEFAULT,
		.server_message_get_callback = NULL,
		.server_message_set_callback = NULL,
		.app_init_callback = NULL,
		.app_main_callback = NULL
	};

	return config_default;
}

static uint8_t wifi_framework_initialized = 0;

static uint16_t wifi_conn_clock_s;
static uint16_t application_clock_s;

uint8_t wifi_framework_init(struct wifi_framework_config wac) {
	config = wac;

	wifi_conn_clock_s = 0;
	application_clock_s = 0;

	if (!wifi_framework_initialized) {
		load_metadata(&metadata);
		timer8_init(1000, 1);
		ESP8266_link_init(&esp_params, server_message_buf, SERVER_MSG_SIZE_MAX, config.server_latency_timeout);

		wifi_framework_initialized = 1;
	}

	return ARDUINO_WIFI_SUCCESS;
}

void wifi_framework_start(void) {
	module_startup_procedure();

	if (config.app_init_callback != NULL) config.app_init_callback();

	module_check();

	timer8_init(1000, 1);
	timer8_start();

	for (;;) {
		if (timer8_flag) {
			wifi_conn_clock_s += timer8_flag;
			application_clock_s += timer8_flag;
			timer8_restart();
		}

		if (wifi_conn_clock_s >= config.connection_interval) {
			module_check();
			wifi_conn_clock_s = 0;
		}

		if (application_clock_s >= config.application_interval) {
			if (config.app_main_callback != NULL) config.app_main_callback();
			application_clock_s = 0;
		}

		ESP8266_poll(&esp_params, 100);

		process_server_message();
	}
}
