#ifndef ARDUINO_WIFI_FRAMEWORK_H
#define ARDUINO_WIFI_FRAMEWORK_H

#include <stdint.h>

#define ARDUINO_WIFI_SUCCESS 0
#define ARDUINO_WIFI_ERROR 1

#define WIFI_STARTUP_TIMEOUT_DEFAULT 10
#define APPLICATION_INTERVAL_DEFAULT 30
#define CONNECTION_INTERVAL_DEFAULT 60
#define CMD_RETRIES_DEFAULT 2
#define CMD_TIMEOUT_DEFAULT 1500
#define SERVER_LATENCY_TIMEOUT_DEFAULT 3
#define SERVER_MSG_SIZE_MAX 32

/*
	All timeouts/intervals are in units of seconds except command_timeout and 
	  server_latency_timeout.

	Wifi app can be re-initialized at any time and will respect changes to any parameter
	  that differes from the original init arguments except server_latency_timeout.
*/
struct wifi_framework_config {
	uint16_t wifi_startup_timeout; // Keep under 60s to maintain system timing integrity.
	uint16_t application_interval;
	uint16_t connection_interval;
	uint16_t command_retries;
	uint16_t command_timeout;
	uint8_t server_latency_timeout;
	uint32_t (* server_message_get_callback)(uint16_t reg);
	uint32_t (* server_message_set_callback)(uint16_t reg, uint32_t val);
	void (* app_init_callback)(void);
	void (* app_main_callback)(void);
};

struct wifi_framework_config wifi_framework_config_create(void);

uint8_t wifi_framework_init(struct wifi_framework_config);

void wifi_framework_start(void);

uint8_t wifi_send(char*);

#endif
