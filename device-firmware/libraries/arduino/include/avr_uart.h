/*
Author: Braeden Mulligan
        braeden.mulligan@gmail.com
*/
#include <stdint.h>

#define RX_BUFFER_SIZE 128

void uart_init(uint16_t baud_rate);

uint16_t uart_available(void);

char uart_getc(void);

void uart_puts(char* s);

void uart_flush(void);
