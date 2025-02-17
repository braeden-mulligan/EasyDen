#include <stdint.h>

#ifndef AVR_ESP8266_LINK_H
#define AVR_ESP8266_LINK_H

#define ESP8266_RECV_FALSE 0
#define ESP8266_RECV_MODULE 1
#define ESP8266_RECV_SERVER 2
#define ESP8266_RECV_BUFOVERFLOW 3
#define ESP8266_RECV_SERVERTIMEOUT 4
#define ESP8266_RECV_ERROR 5

#define ESP8266_CMD_SUCCESS 10
#define ESP8266_CMD_FAILURE 11
#define ESP8266_CMD_CONTINUE 12
#define ESP8266_CMD_TIMEOUT 13
#define ESP8266_CMD_SENDREADY 14
#define ESP8266_CMD_ERROR 15

#define ESP8266_MODULE_NOTIFICATION 20
#define ESP8266_MODULE_BUSY 21
#define ESP8266_MESSAGE_NONE 22

#define ESP8266_STATUS_UPDATE 30
#define ESP8266_ERROR_UNKNOWN 69
#define ESP8266_NULL 255

#define ESP8266_MODE_STATION 1
#define ESP8266_MODE_SOFTAP 2
#define ESP8266_MODE_BOTH 3

#define ESP8266_UART_BAUD 57600
#define ESP8266_LINE_MAX_SIZE 127

struct ESP8266_network_parameters {
	int8_t module_ready;
	int8_t command_echo;
	int8_t multiplexing;
	int8_t wifi_mode; // 1 => station, 2 => softAP, 3 => softAP+station
	int8_t lan_connection;
	int8_t ip_obtained;
	int8_t tcp_connection;
};

// Pass a buffer for server messages, the buffer size, and allotted time for a tcp message.
void ESP8266_link_init(struct ESP8266_network_parameters*, char*, uint8_t, uint8_t);

void ESP8266_reset_serial(void);

uint8_t server_message_available(void);

void server_message_dequeue(void);

// All following functions require timeout for second parameter.
uint8_t ESP8266_poll(struct ESP8266_network_parameters*, uint16_t);

uint8_t ESP8266_ping(struct ESP8266_network_parameters*, uint16_t);

uint8_t ESP8266_echo_disable(struct ESP8266_network_parameters*, uint16_t);

uint8_t ESP8266_status(struct ESP8266_network_parameters*, uint16_t);

uint8_t ESP8266_wifi_mode_get(struct ESP8266_network_parameters*, uint16_t);

uint8_t ESP8266_wifi_mode_set(struct ESP8266_network_parameters*, uint16_t);

uint8_t ESP8266_lan_connect(struct ESP8266_network_parameters*, uint16_t, char* wifi_ssid, char* wifi_pass);

uint8_t ESP8266_ap_query(struct ESP8266_network_parameters*, uint16_t, char* target_wifi_ssid, uint8_t* matched_ssid);

uint8_t ESP8266_socket_connect(struct ESP8266_network_parameters*, uint16_t, char* socket_addr, char* socket_port);

uint8_t ESP8266_socket_send(struct ESP8266_network_parameters*, uint16_t, char* message_buffer);

uint8_t ESP8266_lan_disconnect(struct ESP8266_network_parameters*, uint16_t);

#endif
