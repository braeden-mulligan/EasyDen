#include <stdint.h>

#ifndef AVR_ESP8266_LINK_H
#define AVR_ESP8266_LINK_H

#define ESP8266_RECV_FALSE 0
#define ESP8266_RECV_TRUE 1
#define ESP8266_RECV_SERVER 2
#define ESP8266_RECV_BUFOVERFLOW 3
#define ESP8266_RECV_TIMEOUT 4
#define ESP8266_RECV_SERVERTIMEOUT 5
#define ESP8266_MODULE_NOTIFICATION 6
#define ESP8266_MESSAGE_NONE 7
#define ESP8266_CMD_SUCCESS 10
#define ESP8266_CMD_FAILURE 11
#define ESP8266_CMD_CONTINUE 12
#define ESP8266_CMD_UNKNOWN 13
#define ESP8266_UNKNOWN_ERROR 69

#define ESP8266_LINE_MAX_SIZE 127

struct ESP8266_network_parameters {
	int8_t module_ready;
	int8_t multiplexing;
	int8_t wifi_mode; // 1 => station, 2 => softAP, 3 => softAP+station
	int8_t lan_connection;
	int8_t ip_obtained;
	int8_t tcp_connection;
};

// Pass a buffer for server messages and the buffer size.
void ESP8266_link_init(struct ESP8266_network_parameters*, char*, uint8_t);

uint8_t ESP8266_recv(void);

uint8_t ESP8266_ping(struct ESP8266_network_parameters*, uint16_t timeout_ms);

uint8_t ESP8266_echo_disable(struct ESP8266_network_parameters*, int16_t timeout_ms);

#endif
