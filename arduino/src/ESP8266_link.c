#include "ESP8266_link.h"
#include "avr_uart.h"
#include "avr_utilities.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <util/delay.h>

#define ESP8266_UART_TIMEOUT 1

static uint8_t line_ptr;

static char ESP8266_line_incoming[ESP8266_LINE_MAX_SIZE + 1];

static char* server_message_buffer;
static uint8_t server_message_size;
static uint8_t server_message_timeout;
static uint8_t server_message_queued;

void ESP8266_link_init(struct ESP8266_network_parameters* np, char* server_msg_buf, uint8_t n_msg_buf, uint8_t msg_timeout) {
	uart_init(ESP8266_UART_BAUD);

	line_ptr = 0;
	memset(ESP8266_line_incoming, '\0', ESP8266_LINE_MAX_SIZE + 1);

	if (np != NULL) {
		np->module_ready = 0;
		np->command_echo = 1;
		np->multiplexing = -1;
		np->wifi_mode = 0; 
		np->lan_connection = 0;
		np->ip_obtained = 0;
		np->tcp_connection = 0;
	}

	server_message_buffer = server_msg_buf;
	server_message_size = n_msg_buf;
	server_message_timeout = msg_timeout;
}

void ESP8266_reset_serial(void) {
	_delay_ms(500);
	uart_flush();
	_delay_ms(500);
}


uint8_t ESP8266_recv(void) {
	char c;

	while (uart_available()) {
		c = uart_getc();

		if (c != '\r') ESP8266_line_incoming[line_ptr] = c;

		if (c == '\n') {
			ESP8266_line_incoming[line_ptr] = '\0';
			if (line_ptr == 0) return ESP8266_RECV_FALSE;

// Leading whitespace after a tcp send
			if (line_ptr == 1 && ESP8266_line_incoming[0] == ' ' ) {
				line_ptr = 0;
				return ESP8266_RECV_FALSE;
			}

			line_ptr = 0;
			return ESP8266_RECV_TRUE;
		}

		if (c != '\r') ++line_ptr;

		if (line_ptr >= ESP8266_LINE_MAX_SIZE) {
			line_ptr = 0;
			return ESP8266_RECV_BUFOVERFLOW;
		}

// Edge case for AT+CIPSEND
// TODO: leading whitespace issue?
		if (c == '>') {
			ESP8266_line_incoming[line_ptr] = '\0';
			line_ptr = 0;
			return ESP8266_RECV_TRUE;
		}

// Unprompted server messages;
		char * server_message_start;
		if ((server_message_start = strstr(ESP8266_line_incoming, "+IPD,")) != NULL) {
			int8_t message_bytes = 0;

			for (uint16_t i = 0; i < ESP8266_UART_TIMEOUT * 100; ++i) {
				while (uart_available()) {
					c = uart_getc();

					if (c == ':') {
						message_bytes = strtol(server_message_start + 5, NULL, 10);
						line_ptr = 0;
						continue;
					} 

					ESP8266_line_incoming[line_ptr] = c;
					++line_ptr;

					if (message_bytes && (line_ptr >= message_bytes)) {
						ESP8266_line_incoming[line_ptr] = '\0';
						line_ptr = 0;
						return ESP8266_RECV_SERVER;
					}

					if (line_ptr >= ESP8266_LINE_MAX_SIZE) {
						line_ptr = 0;
						return ESP8266_RECV_BUFOVERFLOW;
					}
					
					if (i > 1) --i;
				} 

				_delay_us(10);
			}

			line_ptr = 0;
			return ESP8266_RECV_SERVERTIMEOUT;
		}

		ESP8266_line_incoming[line_ptr] = '\0';
	}

	return ESP8266_RECV_FALSE;
}

static void server_message_enqueue(void) {
	if (!server_message_queued && server_message_buffer != NULL) {
		strncpy(server_message_buffer, ESP8266_line_incoming, server_message_size);
		server_message_queued = 1;
	}
}

uint8_t server_message_available(void) {
	return server_message_queued;
}

void server_message_dequeue(void) {
	server_message_queued = 0;
}

static uint8_t check_module_notification(struct ESP8266_network_parameters* np) {
	if (strstr(ESP8266_line_incoming, "ready") != NULL) {
		np->module_ready = 1;
		return ESP8266_MODULE_NOTIFICATION;

	} else if (strstr(ESP8266_line_incoming, "WIFI CONNECTED") != NULL) {
		np->lan_connection = 1;
		return ESP8266_MODULE_NOTIFICATION;

	} else if (strstr(ESP8266_line_incoming, "WIFI DISCONNECT") != NULL) {
		np->lan_connection = 0;
		return ESP8266_MODULE_NOTIFICATION;

	} else if (strstr(ESP8266_line_incoming, "WIFI GOT IP") != NULL) {
		np->ip_obtained = 1;
		return ESP8266_MODULE_NOTIFICATION;

	} else if (strstr(ESP8266_line_incoming, "CONNECT") != NULL) {
		np->tcp_connection= 1;
		return ESP8266_MODULE_NOTIFICATION;

	} else if (strstr(ESP8266_line_incoming, "CLOSED") != NULL) {
		np->tcp_connection = 0;
		return ESP8266_MODULE_NOTIFICATION;

	} else if (strstr(ESP8266_line_incoming, "busy s...") != NULL) {
		return ESP8266_MODULE_BUSY;

	} else if (strstr(ESP8266_line_incoming, "busy p...") != NULL) {
		return ESP8266_MODULE_BUSY;

	} else if (strstr(ESP8266_line_incoming, "ERROR") != NULL) {
		return ESP8266_ERROR_UNKNOWN;
	}

	return ESP8266_MESSAGE_NONE;
}

/*
	ESP8266_poll
	Possible return values:
ESP8266_RECV_FALSE:
ESP8266_RECV_TRUE:
ESP8266_RECV_SERVER:
ESP8266_RECV_BUFOVERFLOW
ESP8266_RECV_SERVERTIMEOUT
ESP8266_MODULE_NOTIFICATION
ESP8266_MODULE_BUSY
ESP8266_ERROR_UNKNOWN
*/
uint8_t ESP8266_poll(struct ESP8266_network_parameters* np, uint32_t timeout_ms) {
	uint8_t retval = ESP8266_RECV_FALSE;
	uint8_t module_message;

	for (uint32_t i = 0; i < timeout_ms * 100; ++i) {
		retval = ESP8266_recv();

		switch (retval) {
		case ESP8266_RECV_FALSE:
			_delay_us(10);
			continue;

		case ESP8266_RECV_TRUE:
			module_message = check_module_notification(np);
			if (module_message != ESP8266_MESSAGE_NONE) return module_message;
			return ESP8266_RECV_TRUE;

		case ESP8266_RECV_SERVER:
			server_message_enqueue();
			return ESP8266_RECV_SERVER;

		case ESP8266_RECV_BUFOVERFLOW:
		case ESP8266_RECV_SERVERTIMEOUT:
		default:
			return retval;
		}
	}

	return retval;
}

/*
		run_cmd
	Possible return values:
	ESP8266_CMD_SUCCESS
	ESP8266_CMD_FAILURE
	ESP8266_CMD_CONTINUE
	ESP8266_CMD_SENDREADY
	ESP8266_CMD_TIMEOUT
	ESP8266_CMD_ERROR
*/
static uint8_t run_cmd(uint8_t (* cmd_proc)(struct ESP8266_network_parameters*), char* cmd, struct ESP8266_network_parameters* np, uint32_t timeout_ms) {
	uint8_t retval = ESP8266_RECV_FALSE;
	uint8_t cmd_status;
	uint8_t module_message;

	uart_puts(cmd);

	for (uint32_t i = 0; i < timeout_ms * 100; ++i) {
		retval = ESP8266_recv();

		switch (retval) {
		case ESP8266_RECV_FALSE:
			break;

		case ESP8266_RECV_TRUE:
			module_message = check_module_notification(np);
			if (module_message == ESP8266_MODULE_NOTIFICATION) break;
			if (module_message == ESP8266_MODULE_BUSY) break;
			if (module_message == ESP8266_ERROR_UNKNOWN) return ESP8266_CMD_ERROR;

			cmd_status = cmd_proc(np);
			if (cmd_status == ESP8266_CMD_CONTINUE) break;
			if (cmd_status == ESP8266_CMD_SUCCESS) return ESP8266_CMD_SUCCESS;
			if (cmd_status == ESP8266_CMD_FAILURE) return ESP8266_CMD_FAILURE;
			if (cmd_status == ESP8266_CMD_SENDREADY) return ESP8266_CMD_SENDREADY;
			break;

		case ESP8266_RECV_SERVER:
			server_message_enqueue();
			break;

		case ESP8266_RECV_BUFOVERFLOW:
		case ESP8266_RECV_SERVERTIMEOUT:
		default:
			return ESP8266_CMD_ERROR;
		}

		_delay_us(10);
	}

	return ESP8266_CMD_TIMEOUT;
}

static uint8_t parse_ok(void) {
	if (strstr(ESP8266_line_incoming, "OK") != NULL) return 1;
	return 0;
}

static uint8_t _ESP8266_ping(struct ESP8266_network_parameters* np) {
	if (parse_ok()) {
		np->module_ready = 1;
		return ESP8266_CMD_SUCCESS;

	} else if (strstr(ESP8266_line_incoming, "AT") != NULL) {
		return ESP8266_CMD_CONTINUE;
	}

	return ESP8266_CMD_FAILURE;
}
uint8_t ESP8266_ping(struct ESP8266_network_parameters* np, uint32_t timeout_ms) {
	char* cmd = "AT\r\n"; 
	return run_cmd(_ESP8266_ping, cmd, np, timeout_ms);
}

static uint8_t _ESP8266_echo_disable(struct ESP8266_network_parameters* np) {
	if (parse_ok()) {
		np->command_echo = 0;
		return ESP8266_CMD_SUCCESS;

	} else if (strstr(ESP8266_line_incoming, "ATE0") != NULL) {
		return ESP8266_CMD_CONTINUE;
	}

	return ESP8266_CMD_FAILURE;
}
uint8_t ESP8266_echo_disable(struct ESP8266_network_parameters* np, uint32_t timeout_ms) {
	char* cmd = "ATE0\r\n"; 
	return run_cmd(_ESP8266_echo_disable, cmd, np, timeout_ms);
}

static uint8_t _ESP8266_status(struct ESP8266_network_parameters* np) {
	if (parse_ok()) {
		return ESP8266_CMD_SUCCESS;

	} else if (strstr(ESP8266_line_incoming, "CIPSTATUS") != NULL) {
		return ESP8266_CMD_CONTINUE;

	} else if (strstr(ESP8266_line_incoming, "STATUS:2") != NULL) {
		np->lan_connection = 1;
		np->ip_obtained = 1;
		return ESP8266_CMD_CONTINUE;

	} else if (strstr(ESP8266_line_incoming, "STATUS:3") != NULL) {
		np->lan_connection = 1;
		np->ip_obtained = 1;
		np->tcp_connection = 1;
		return ESP8266_CMD_CONTINUE;

	} else if (strstr(ESP8266_line_incoming, "STATUS:4") != NULL) {
		np->tcp_connection = 0;
		return ESP8266_CMD_CONTINUE;

	} else if (strstr(ESP8266_line_incoming, "STATUS:5") != NULL) {
		np->lan_connection = 0;
		np->ip_obtained = 0;
		np->tcp_connection = 0;
		return ESP8266_CMD_CONTINUE;
	}

	return ESP8266_CMD_FAILURE;
}
uint8_t ESP8266_status(struct ESP8266_network_parameters* np, uint32_t timeout_ms) {
	char* cmd = "AT+CIPSTATUS\r\n";
	return run_cmd(_ESP8266_status, cmd, np, timeout_ms);
}

static uint8_t _ESP8266_wifi_mode(struct ESP8266_network_parameters* np) {
	if (parse_ok()) {
		return ESP8266_CMD_SUCCESS;

	} else if (strstr(ESP8266_line_incoming, "CWMODE_CUR?") != NULL) {
		return ESP8266_CMD_CONTINUE;

	} else if (strstr(ESP8266_line_incoming, "CWMODE_DEF") != NULL) {
		return ESP8266_CMD_CONTINUE;

	} else if (strstr(ESP8266_line_incoming, "CWMODE_CUR:1") != NULL) {
		np->wifi_mode = 1;
		return ESP8266_CMD_CONTINUE;

	} else if (strstr(ESP8266_line_incoming, "CWMODE_CUR:2") != NULL) {
		np->wifi_mode = 2;
		return ESP8266_CMD_CONTINUE;

	} else if (strstr(ESP8266_line_incoming, "CWMODE_CUR:3") != NULL) {
		np->wifi_mode = 3;
		return ESP8266_CMD_CONTINUE;
	}

	return ESP8266_CMD_FAILURE;
}
uint8_t ESP8266_wifi_mode_get(struct ESP8266_network_parameters* np, uint32_t timeout_ms) {
	char* cmd = "AT+CWMODE_CUR?\r\n";
	return run_cmd(_ESP8266_wifi_mode, cmd, np, timeout_ms);
}

uint8_t ESP8266_wifi_mode_set(struct ESP8266_network_parameters* np, uint32_t timeout_ms) {
	char* cmd = "AT+CWMODE_DEF=1\r\n";

	uint8_t result = run_cmd(_ESP8266_wifi_mode, cmd, np, timeout_ms);
	if (result == ESP8266_CMD_SUCCESS) np->wifi_mode = ESP8266_MODE_STATION;

	return result;
}

static uint8_t _ESP8266_lan_connect(struct ESP8266_network_parameters* np) {
	if (parse_ok()) {
		return ESP8266_CMD_SUCCESS;

	} else if (strstr(ESP8266_line_incoming, "CWJAP_CUR") != NULL) {
		return ESP8266_CMD_CONTINUE;
	}

	return ESP8266_CMD_FAILURE;
}
uint8_t ESP8266_lan_connect(struct ESP8266_network_parameters* np, uint32_t timeout_ms, char* wifi_ssid, char* wifi_pass) {
	char cmd[64];
	sprintf(cmd, "AT+CWJAP_CUR=\"%s\",\"%s\"\r\n", wifi_ssid, wifi_pass);
	return run_cmd(_ESP8266_lan_connect, cmd, np, timeout_ms);
}

static uint8_t _ESP8266_socket_connect(struct ESP8266_network_parameters* np) {
	if (parse_ok()) {
		return ESP8266_CMD_SUCCESS;

	} else if (strstr(ESP8266_line_incoming, "CIPSTART") != NULL) {
		return ESP8266_CMD_CONTINUE;

	} else if (strstr(ESP8266_line_incoming, "no ip") != NULL) {
		np->ip_obtained = 0;
		return ESP8266_CMD_CONTINUE;
	}

	return ESP8266_CMD_FAILURE;
}
uint8_t ESP8266_socket_connect(struct ESP8266_network_parameters* np, uint32_t timeout_ms, char* socket_addr, char* socket_port) {
	char cmd[64];
	sprintf(cmd, "AT+CIPSTART=\"TCP\",\"%s\",%s\r\n", socket_addr, socket_port);
	return run_cmd(_ESP8266_socket_connect, cmd, np, timeout_ms);
}

static uint8_t _ESP8266_socket_send(struct ESP8266_network_parameters* np) {
	if (parse_ok() && strstr(ESP8266_line_incoming, "SEND OK") == NULL) {
		return ESP8266_CMD_CONTINUE;

	} else if (strstr(ESP8266_line_incoming, "CIPSEND") != NULL) {
		return ESP8266_CMD_CONTINUE;

	} else if (strstr(ESP8266_line_incoming, "link is not valid") != NULL) {
		np->tcp_connection = 0;
		return ESP8266_CMD_CONTINUE;

	} else if (strstr(ESP8266_line_incoming, "no ip") != NULL) {
		np->ip_obtained = 0;
		np->tcp_connection = 0;
		return ESP8266_CMD_CONTINUE;

	} else if (strstr(ESP8266_line_incoming, ">") != NULL) {
		return ESP8266_CMD_SENDREADY;

	} else if (strstr(ESP8266_line_incoming, "Recv") != NULL) {
		return ESP8266_CMD_CONTINUE;

	} else if (strstr(ESP8266_line_incoming, "SEND OK") != NULL) {
		return ESP8266_CMD_SUCCESS;
	}
	
	return ESP8266_CMD_FAILURE;
}
uint8_t ESP8266_socket_send(struct ESP8266_network_parameters* np, uint32_t timeout_ms, char* message_buffer) {
	uint8_t result;
	char cmd[24];
	sprintf(cmd, "AT+CIPSEND=%d\r\n", strlen(message_buffer));

	result = run_cmd(_ESP8266_socket_send, cmd, np, timeout_ms);

	if (result == ESP8266_CMD_SENDREADY) {
		result = run_cmd(_ESP8266_socket_send, message_buffer, np, timeout_ms);
	} else {
	
	}

	return result;
}

