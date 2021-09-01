/*
 * Author: Braeden Mulligan
 *         braeden.mulligan@gmail.com
 *
 * Copyright: GNU GPL Version 3
 *
 */
#include "avr_timer_util.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/atomic.h>

static uint16_t timer8_cycle_count = 0;
static uint16_t timer8_period = 0;

void timer8_init(uint16_t period_ms) {
	timer8_period = period_ms;

	ATOMIC_BLOCK(ATOMIC_FORCEON) {
		timer8_flag = false;

		// This gives us approximate number of clock ticks for 1ms with 1024 prescaler. 
		OCR0A = 16;
		TCCR0A |= (1 << WGM01);
		TIMSK0 |= (1 << OCIE0A); 
	}
}

inline void timer8_start(void) {
	ATOMIC_BLOCK(ATOMIC_FORCEON) {
		timer8_flag = false;
		timer8_cycle_count = 0;
		TCCR0B |= (1 << CS02) | (1 << CS00);
	}
}

inline void timer8_stop(void) {
	ATOMIC_BLOCK(ATOMIC_FORCEON) {
		TCCR0B &= ~((1 << CS02) | (1 << CS00));
		TCNT0 = 0;
	}
}

void timer8_reset(void) {
	timer8_stop();
	timer8_start();
}

ISR(TIMER0_COMPA_vect) {
	if (timer8_cycle_count < timer8_period) {
		++timer8_cycle_count;
	} else {
		timer8_flag = true;
		timer8_cycle_count = 0;
	}
}

static uint16_t timer16_cycle_count = 0;
static uint16_t timer16_period = 0;

void timer16_init(uint16_t period_s) {
	timer16_period = period_s - 1;

	ATOMIC_BLOCK(ATOMIC_FORCEON) {
		timer16_flag = false;

		TCCR1B |= (1 << WGM12); 
		// Count clock ticks to 1 second.
		OCR1A = 15625;
		TIMSK1 |= (1 << OCIE1A); 
	}
}

void timer16_start(void) {
	ATOMIC_BLOCK(ATOMIC_FORCEON) {
		timer16_flag = false;
		timer16_cycle_count = 0;
		TCCR1B |= (1 << CS10) | (1 << CS12);
	}
}

void timer16_stop(void) {
	ATOMIC_BLOCK(ATOMIC_FORCEON) {
		TCCR1B &= ~((1 << CS10) | (1 << CS12));
		TCNT1 = 0;
	}
}

void timer16_reset(void) {
	timer16_stop();
	timer16_start();
}

ISR(TIMER1_COMPA_vect) {
	if (timer16_cycle_count < timer16_period) {
		++timer16_cycle_count;
	} else {
		timer16_flag = true;
		timer16_cycle_count = 0;
	}
}
