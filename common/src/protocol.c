#include "device_definition.h"
#include "protocol.h"

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

static uint16_t seq_num = 0;

uint16_t generate_seq(void) {
	++seq_num;
	if (!seq_num) ++seq_num;
	return seq_num;
}
	
// <seq, cmd, reg, val>
uint8_t sh_parse_packet(struct sh_packet* p, char* msg_buf) {
	char* end;

	p->seq = (uint16_t)strtol(msg_buf, &end, 16);
	if (end == NULL) return SH_PROTOCOL_ERROR;
	++end;

	p->cmd = (uint8_t)strtol(end, &end, 16);
	if (end == NULL) return SH_PROTOCOL_ERROR;
	++end;

	p->reg = (uint8_t)strtol(end, &end, 16);
	if (end == NULL) return SH_PROTOCOL_ERROR;
	++end;

	p->val = (int32_t)strtol(end, &end, 16);
	if (end == NULL) return SH_PROTOCOL_ERROR;
	
	return SH_PROTOCOL_SUCCESS;
}

uint8_t sh_build_packet(struct sh_packet* p, char* msg_buf) {
#if defined (__AVR_ATmega328P__)
	if (sprintf(msg_buf, "%04X,%02X,%02X,%08lX", p->seq, p->cmd, p->reg, p->val) < 0) return SH_PROTOCOL_ERROR;
#else
	if (sprintf(msg_buf, "%04X,%02X,%02X,%08X", p->seq, p->cmd, p->reg, p->val) < 0) return SH_PROTOCOL_ERROR;
#endif
	return SH_PROTOCOL_SUCCESS;
}

/*
uint8_t sh_build_data_packet(struct sh_data_packet* p, char* msg_buf) {
	if (p->len > DATA_LEN_MAX) return SH_PROTOCOL_ERROR;

	sprintf(msg_buf, "%04X,%02X,%04X,", p->seq, p->cmd, p->len);

	char data_byte[4];
	for (uint16_t i = 0; i < p->len; ++i) {
		sprintf(data_byte, "%02X", p->dat[i]); 
		strcat(msg_buf, data_byte);
	}

	return SH_PROTOCOL_SUCCESS;
}
*/
