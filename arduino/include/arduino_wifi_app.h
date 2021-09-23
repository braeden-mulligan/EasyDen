#ifndef ARDUINO_WIFI_APP_H
#define ARDUINO_WIFI_APP_H

#include <stdint.h>

#define ARDUINO_APP_SUCCESS 0
#define ARDUINO_APP_ERROR 1

#define WIFI_STARTUP_TIMEOUT_DEFAULT 5
#define APPLICATION_INTERVAL_DEFAULT 60
#define CMD_RETRIES_DEFAULT 2
#define CMD_TIMEOUT_DEFAULT 2000
#define SERVER_LATENCY_TIMEOUT_DEFAULT 3
#define SERVER_BUF_SIZE_DEFAULT 0

struct wifi_app_config {
	uint16_t wifi_startup_timeout;
	uint16_t application_interval;
	uint16_t command_retries;
	uint16_t command_timeout;
	uint8_t server_latency_timeout;
	uint8_t server_buf_size;
	char* server_message_buf;
	void (* server_message_callback)(void);
	void (* app_main_callback)(void);
};

void app_error_check(uint8_t retval);

struct wifi_app_config wifi_app_config_create(void);

uint8_t wifi_app_init(struct wifi_app_config* wac);

void wifi_app_start(void);

uint8_t wifi_send(char* message);

#endif
