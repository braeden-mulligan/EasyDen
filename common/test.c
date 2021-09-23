#include <stdio.h>

#include "protocol.h"

struct sh_packet p = {
	.seq = 1,
	.cmd = 3,
	.reg = 2,
	.val = 420
};

uint8_t data[7] = {52, 44, 69, 23, 99, 0, 200};

struct sh_data_packet p2 = {
	.seq = 5,
	.cmd = CMD_DAT,
	.len = 7,
	.dat = data
};

int main(void) {

	char buf[512];
		
	sh_build_packet(&p, buf);
	printf("packet:[%s]\n", buf);

	struct sh_packet new_p;
	sh_parse_packet(&new_p, buf);
	printf("%02x,%02X,%02x,%08x\n", new_p.seq, new_p.cmd, new_p.reg, new_p.val);

	sh_build_data_packet(&p2, buf);
	printf("data packet:[%s]\n", buf);
	



}

