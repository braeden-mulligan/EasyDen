#include "device_catalogue.h"
#include "protocol.h"

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

static uint16_t seq_num = 0;

static uint8_t get_int(int32_t* num, char** buf) {
	char* end;
	*num = (int32_t)strtol(*buf, &end, 16);
	if (end == NULL) return SH_PARSE_ERROR;

	*buf = end;

	return SH_PARSE_SUCCESS;
}

static void increment_seq_num(void) {
	++seq_num;
	if (!seq_num) ++seq_num;
}
	

// <seq, cmd, reg, val>
uint8_t sh_parse_packet(struct sh_packet* p, char* msg_buf) {
	if (get_int((uint32_t*)&(p->seq), &msg_buf) == SH_PARSE_ERROR) return SH_PARSE_ERROR;
	++msg_buf;
	if (get_int((uint32_t*)&(p->cmd), &msg_buf) == SH_PARSE_ERROR) return SH_PARSE_ERROR;
	++msg_buf;
	if (get_int((uint32_t*)&(p->reg), &msg_buf) == SH_PARSE_ERROR) return SH_PARSE_ERROR;
	++msg_buf;
	if (get_int(&(p->val), &msg_buf) == SH_PARSE_ERROR) return SH_PARSE_ERROR;
	return SH_PARSE_SUCCESS;
}

uint8_t sh_build_packet(struct sh_packet* p, char* msg_buf) {
	switch (p->cmd) {
		case CMD_PSH:
			increment_seq_num();
			break;
		case CMD_RSP:
			break;
		default:
			return SH_PARSE_ERROR;
	}

#if defined (__AVR_ATmega328P__)
	if (sprintf(msg_buf, "%04X,%02X,%02X,%08lX", p->seq, p->cmd, p->reg, p->val) < 0) return SH_PARSE_ERROR;
#else
	if (sprintf(msg_buf, "%04X,%02X,%02X,%08X", p->seq, p->cmd, p->reg, p->val) < 0) return SH_PARSE_ERROR;
#endif
	return SH_PARSE_SUCCESS;
}

uint8_t sh_build_data_packet(struct sh_data_packet* p, char* msg_buf) {
	if (p->len > DATA_LEN_MAX) return SH_PARSE_ERROR;

	sprintf(msg_buf, "%04X,%02X,%04X,", p->seq, p->cmd, p->len);

	char data_byte[4];
	for (uint16_t i = 0; i < p->len; ++i) {
		sprintf(data_byte, "%02X", p->dat[i]); 
		strcat(msg_buf, data_byte);
	}

	return SH_PARSE_SUCCESS;
}
