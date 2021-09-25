#ifndef ARDUINO_WIFI_APP_H
#define ARDUINO_WIFI_APP_H

#include <stdint.h>

#define ARDUINO_APP_SUCCESS 0
#define ARDUINO_APP_ERROR 1

#define WIFI_STARTUP_TIMEOUT_DEFAULT 5
#define APPLICATION_INTERVAL_DEFAULT 30
#define CONNECTION_INTERVAL_DEFAULT 60
#define CMD_RETRIES_DEFAULT 2
#define CMD_TIMEOUT_DEFAULT 1000
#define SERVER_LATENCY_TIMEOUT_DEFAULT 3
#define SERVER_BUF_SIZE_DEFAULT 0

/*
	All timeouts/intervals are in units of seconds except command_timeout and 
	  server_latency_timeout.

	Wifi app can be re-initialized at any time and will respect changes to any parameter
	  that differes from the original init arguments except server_latency_timeout, 
	  server_message_buf, server_buf_size.
*/
struct wifi_app_config {
	uint16_t wifi_startup_timeout; // Keep under 60s to maintain system timing integrity.
	uint16_t application_interval;
	uint16_t connection_interval;
	uint16_t command_retries;
	uint16_t command_timeout;
	uint8_t server_latency_timeout;
	uint8_t server_buf_size;
	char* server_message_buf;
	void (* server_message_callback)(void);
	void (* app_main_callback)(void);
};

void app_error_check(uint8_t);

struct wifi_app_config wifi_app_config_create(void);

uint8_t wifi_app_init(struct wifi_app_config*);

void wifi_app_start(void);

uint8_t wifi_send(char*);

#endif
