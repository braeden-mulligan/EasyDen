#ifndef SH_PROTOCOL_H
#define SH_PROTOCOL_H

#include <stdint.h>

#define SH_PROTOCOL_SUCCESS 0
#define SH_PROTOCOL_ERROR 1

#define CMD_NUL 0
#define CMD_GET 1
#define CMD_SET 2
#define CMD_RSP 3
#define CMD_PSH 4
#define CMD_IDY 5
//#define CMD_DAT 6

// max packet length 1024 including header.
//#define DATA_LEN_MAX 1010

struct sh_packet {
	uint16_t seq;
	uint8_t cmd; 
	uint8_t reg; // (type)
	uint32_t val; // (id)
};

/*
struct sh_data_packet {
	uint8_t seq;
	uint8_t cmd; 
	uint16_t len;
	uint8_t* dat;
};
*/

uint16_t generate_seq(void);

uint8_t sh_parse_packet(struct sh_packet*, char* msg_buf);

uint8_t sh_build_packet(struct sh_packet*, char* msg_buf);

//uint8_t sh_build_data_packet(struct sh_data_packet*, char* msg_buf);

#endif
