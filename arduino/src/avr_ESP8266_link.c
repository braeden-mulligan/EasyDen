#include "avr_ESP8266_link.h"
#include "avr_uart.h"
#include "avr_utilities.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <util/delay.h>

static uint8_t line_ptr;

static char ESP8266_line_incoming[ESP8266_LINE_MAX_SIZE + 1];

static char* server_message_buffer;
static uint8_t server_message_size;
static uint8_t server_message_timeout;

uint8_t ESP8266_recv(void) {
	char c;

	while (uart_available()) {
		c = uart_getc();

		if (c != '\r') ESP8266_line_incoming[line_ptr] = c;

		if (c == '\n') {
			ESP8266_line_incoming[line_ptr] = '\0';
			if (line_ptr == 0) return ESP8266_RECV_FALSE;

			line_ptr = 0;
			return ESP8266_RECV_TRUE;
		}

		if (c != '\r') ++line_ptr;

		if (line_ptr >= ESP8266_LINE_MAX_SIZE) {
			line_ptr = 0;
			return ESP8266_RECV_BUFOVERFLOW;
		}

// Unprompted server messages;
		char * server_message_start;
		if ((server_message_start = strstr(ESP8266_line_incoming, "+IPD,")) != NULL) {
			int8_t message_bytes = 0;

			for (uint8_t i = 0; i < server_message_timeout * 10; ++i) {
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
						return ESP8266_RECV_SERVER;
					}

					if (line_ptr >= ESP8266_LINE_MAX_SIZE) {
						line_ptr = 0;
						return ESP8266_RECV_BUFOVERFLOW;
					}
				} 

				_delay_us(100);
			}

			return ESP8266_RECV_SERVERTIMEOUT;
		}

		ESP8266_line_incoming[line_ptr] = '\0';
	}

	return ESP8266_RECV_FALSE;
}

uint8_t check_module_notification(struct ESP8266_network_parameters* np) {
	if (strstr("ready", ESP8266_line_incoming) != NULL) {
		np->module_ready = 1;
		return ESP8266_MODULE_NOTIFICATION;

	} else if (strstr("WIFI CONNECTED", ESP8266_line_incoming) != NULL) {
		np->lan_connection = 1;
		return ESP8266_MODULE_NOTIFICATION;

	} else if (strstr("WIFI DISCONNECT", ESP8266_line_incoming) != NULL) {
		np->lan_connection = 0;
		return ESP8266_MODULE_NOTIFICATION;

	} else if (strstr("WIFI GOT IP", ESP8266_line_incoming) != NULL) {
		np->ip_obtained = 1;
		return ESP8266_MODULE_NOTIFICATION;

	} else if (strstr("CONNECT", ESP8266_line_incoming) != NULL) {
		np->tcp_connection= 1;
		return ESP8266_MODULE_NOTIFICATION;

	} else if (strstr("CLOSED", ESP8266_line_incoming) != NULL) {
		np->tcp_connection = 0;
		return ESP8266_MODULE_NOTIFICATION;

	} else if (strstr("busy s...", ESP8266_line_incoming) != NULL) {
		return ESP8266_MODULE_BUSY;

	} else if (strstr("busy p...", ESP8266_line_incoming) != NULL) {
		return ESP8266_MODULE_BUSY;

	} else if (strstr("ERROR", ESP8266_line_incoming) != NULL) {
		return ESP8266_UNKNOWN_ERROR;
	}

	return ESP8266_MESSAGE_NONE;
}

//TODO:
uint8_t ESP8266_poll(struct ESP8266_network_parameters* np, uint16_t timeout_ms) {
	uint8_t result = 0;

	for (uint16_t i = 0; i < timeout_ms * 10; ++i) {
		result = ESP8266_recv();

		uint8_t module_message;
		switch (result) {
		case ESP8266_RECV_TRUE:
			module_message = check_module_notification(np);
			if (module_message != ESP8266_MESSAGE_NONE) return module_message;
			break;

		case ESP8266_RECV_SERVER:
			strncpy(server_message_buffer, ESP8266_line_incoming, server_message_size);
			return result;

		default:
			if (result != ESP8266_RECV_FALSE) return result;
			break;
		}

		_delay_us(100);
	}

	return result;
}

static uint8_t run_cmd(uint8_t (* cmd_proc)(struct ESP8266_network_parameters*), char* cmd, struct ESP8266_network_parameters* np, uint16_t timeout_ms) {
	uint8_t retval;

	uart_puts(cmd);

	for (uint16_t i = 0; i < timeout_ms * 10; ++i) {
		retval = ESP8266_recv();

		switch (retval) {
		case ESP8266_RECV_FALSE:
			_delay_us(100);
			continue;

		case ESP8266_RECV_TRUE:
			if (!strcmp("", ESP8266_line_incoming)) continue;

//TODO: Check if ERROR should be handled by command proc
			if (check_module_notification(np) == ESP8266_MODULE_NOTIFICATION) continue;

			uint8_t cmd_status = cmd_proc(np);
			if (cmd_status == ESP8266_CMD_CONTINUE) continue;
			if (cmd_status == ESP8266_CMD_SUCCESS) return ESP8266_CMD_SUCCESS;
			if (cmd_status == ESP8266_CMD_FAILURE) return ESP8266_CMD_FAILURE;
			break;

		case ESP8266_RECV_SERVER:
			strncpy(server_message_buffer, ESP8266_line_incoming, server_message_size);
			return ESP8266_RECV_SERVER;

		case ESP8266_RECV_BUFOVERFLOW:
#ifdef DEBUG_MODE
			blink_led(7, 1000);
#endif
			return retval; 

		default:
#ifdef DEBUG_MODE
			blink_led(-1, 1000);
#endif
			return ESP8266_UNKNOWN_ERROR;
		}
	}

	return ESP8266_RECV_TIMEOUT;
}

static uint8_t parse_ok(void) {
	if (strstr("OK", ESP8266_line_incoming) != NULL) return 1;
	return 0;
}

static uint8_t _ESP8266_ping(struct ESP8266_network_parameters* np) {
	if (parse_ok()) {
		return ESP8266_CMD_SUCCESS;

	} else if (strstr("AT", ESP8266_line_incoming) != NULL) {
		return ESP8266_CMD_CONTINUE;

	}
	return ESP8266_CMD_FAILURE;
}
uint8_t ESP8266_ping(struct ESP8266_network_parameters* np, uint16_t timeout_ms) {
	char* cmd = "AT\r\n"; 
	return run_cmd(_ESP8266_ping, cmd, np, timeout_ms);
}

static uint8_t _ESP8266_echo_disable(struct ESP8266_network_parameters* np) {
	if (parse_ok()) {
		return ESP8266_CMD_SUCCESS;

	} else if (strstr("ATE0", ESP8266_line_incoming) != NULL) {
		return ESP8266_CMD_CONTINUE;

	}
	return ESP8266_CMD_FAILURE;
}
uint8_t ESP8266_echo_disable(struct ESP8266_network_parameters* np, uint16_t timeout_ms) {
	char* cmd = "ATE0\r\n"; 
	return run_cmd(_ESP8266_echo_disable, cmd, np, timeout_ms);
}

uint8_t _ESP8266_status(struct ESP8266_network_parameters* np) {
	if (parse_ok()) {
		return ESP8266_CMD_SUCCESS;

	} else if (strstr("AT+CIPSTATUS", ESP8266_line_incoming) != NULL) {
		return ESP8266_CMD_CONTINUE;

	} else if (strstr("STATUS:2", ESP8266_line_incoming) != NULL) {
		np->lan_connection = 1;
		np->ip_obtained = 1;
		return ESP8266_CMD_CONTINUE;

	} else if (strstr("STATUS:3", ESP8266_line_incoming) != NULL) {
		np->tcp_connection = 1;
		return ESP8266_CMD_CONTINUE;

	} else if (strstr("STATUS:4", ESP8266_line_incoming) != NULL) {
		np->tcp_connection = 1;
		return ESP8266_CMD_CONTINUE;

	} else if (strstr("STATUS:5", ESP8266_line_incoming) != NULL) {
		np->lan_connection = 0;
		np->ip_obtained = 0;
		np->tcp_connection = 0;
		return ESP8266_CMD_CONTINUE;

	}
	return ESP8266_CMD_FAILURE;
}
uint8_t ESP8266_status(struct ESP8266_network_parameters* np, uint16_t timeout_ms) {
	char* cmd = "AT+CIPSTATUS\r\n";
	return run_cmd(_ESP8266_status, cmd, np, timeout_ms);
}

/*
uint8_t _ESP8266_restart(uint16_t timeout_ms) {
	uint8_t retval;

	uart_puts("AT\r\n");

	for (uint16_t i = 0; i < timeout_ms * 10; ++i) {
		_delay_us(100);

		retval = ESP8266_recv();

}
*/

void ESP8266_link_init(struct ESP8266_network_parameters* np, char* server_msg_buf, uint8_t n_msg_buf, uint8_t msg_timeout) {
	uart_init(57600);

	line_ptr = 0;
	memset(ESP8266_line_incoming, '\0', ESP8266_LINE_MAX_SIZE + 1);

	if (np != NULL) {
		np->module_ready = -1;
		np->command_echo = -1;
		np->multiplexing = -1;
		np->wifi_mode = -1; 
		np->lan_connection = -1;
		np->ip_obtained = -1;
		np->tcp_connection = -1;
	}

	server_message_buffer = server_msg_buf;
	server_message_size = n_msg_buf;
	server_message_timeout = msg_timeout;
}

void ESP8266_reset_serial(void) {
	_delay_ms(500);
	uart_flush();
}


