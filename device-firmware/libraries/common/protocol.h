#ifndef ATTR_PROTOCOL_H
#define ATTR_PROTOCOL_H

#include <stdint.h>

#define ATTR_PROTOCOL_SUCCESS 0
#define ATTR_PROTOCOL_ERROR 1

#define CMD_NUL 0
#define CMD_GET 1
#define CMD_SET 2
#define CMD_RSP 3
#define CMD_PSH 4
#define CMD_IDY 5

/**
 * <attr> and <val> represent device type and id respectively when <cmd> is CMD_IDY
 */
struct attr_packet {
	uint16_t seq;
	uint8_t cmd; 
	uint8_t attr; 
	uint32_t val; 
};

uint16_t generate_seq(void);

uint8_t parse_attr_packet(struct attr_packet*, char* msg_buf);

uint8_t build_attr_packet(struct attr_packet*, char* msg_buf);

#endif
