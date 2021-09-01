#include "avr_uart.h"

#include <string.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/atomic.h>

static char rx_buffer[RX_BUFFER_SIZE];

static volatile uint8_t rx_head = 0;
static volatile uint8_t rx_tail = 0;

void uart_init(uint16_t baud) {
	uint16_t baud_prescale = (F_CPU / 16 / baud - 1);
	UBRR0H = (uint8_t)(baud_prescale >> 8);
	UBRR0L = (uint8_t)baud_prescale;

	ATOMIC_BLOCK(ATOMIC_FORCEON) {
		rx_head = 0;
		rx_tail = 0;
	}

	UCSR0C = (1 << UCSZ00) | (1 << UCSZ01);
	UCSR0B = (1 << TXEN0) | (1 << RXEN0) | (1 << RXCIE0);
}

static volatile uint8_t rx_full = 0;

ISR(USART_RX_vect) {
	ATOMIC_BLOCK(ATOMIC_FORCEON) {
		if (!rx_full) {
			rx_buffer[rx_tail] = UDR0;
			++rx_tail;
			//if (rx_tail >= RX_BUFFER_SIZE) rx_tail = 0;
			//if (rx_tail == rx_head) rx_full = 1;
			// Use branchless version for possible performance gain:
			rx_tail = rx_tail - ((rx_tail >= RX_BUFFER_SIZE) * rx_tail);
			rx_full = (rx_tail == rx_head);
		}
	}
}

uint16_t uart_available(void) {
	uint16_t buffer_occupancy = 0;

	ATOMIC_BLOCK(ATOMIC_FORCEON) {
		if (rx_full) {
			buffer_occupancy = RX_BUFFER_SIZE;
		} else {
			if (rx_tail < rx_head) return rx_tail + (RX_BUFFER_SIZE - rx_head);
			buffer_occupancy = (rx_tail - rx_head);
		}
	}

	return buffer_occupancy;
}

char uart_getc(void) {
	char byte = '\0';

	ATOMIC_BLOCK(ATOMIC_FORCEON) {
		if ((rx_head != rx_tail) || rx_full) {
			byte = rx_buffer[rx_head];	
			++rx_head;
			if (rx_head >= RX_BUFFER_SIZE) rx_head = 0;
			rx_full = 0;
		}
	}

	return byte;
}

void uart_puts(char* s) {
	while (*s != '\0') {
		while (!(UCSR0A & (1 << UDRE0))) {}
		UDR0 = *s;
		++s;
	}
}

void uart_flush(void) {
	ATOMIC_BLOCK(ATOMIC_FORCEON) {
		rx_full = 0;
		rx_head = 0;
		rx_tail = 0;
	}
}
