/*
 * Author: Braeden Mulligan
 *         braeden.mulligan@gmail.com
 *
 * Copyright: GNU GPL Version 3
 *
 */
#include "avr_timer_util.h"

#include <stddef.h>
#include <stdint.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/atomic.h>

static uint16_t timer8_cycle_count = 0;
static uint16_t timer8_period = 0;
static uint8_t timer8_initialized = 0;

uint8_t timer8_init(uint16_t period_ms) {
	if (timer8_initialized) return TIMER_INIT_ERROR;

	timer8_period = period_ms;

	ATOMIC_BLOCK(ATOMIC_FORCEON) {
		timer8_flag = 0;

		// This gives us approximate number of clock ticks for 1ms with 1024 prescaler. 
		OCR0A = 16;
		TCCR0A |= (1 << WGM01);
		TIMSK0 |= (1 << OCIE0A); 
	}

	return TIMER_INIT_SUCCESS;
}

inline void timer8_start(void) {
	ATOMIC_BLOCK(ATOMIC_FORCEON) {
		timer8_flag = 0;
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

void timer8_deinit(void) {
	timer8_stop();
	timer8_initialized = 0;
}

ISR(TIMER0_COMPA_vect) {
	if (timer8_cycle_count < timer8_period) {
		++timer8_cycle_count;
	} else {
		timer8_flag += ((timer8_flag + 1) != 0);
		timer8_cycle_count = 0;
	}
}

static uint16_t timer16_cycle_count = 0;
static uint16_t timer16_period = 0;
static uint8_t timer16_initialized = 0;

uint8_t timer16_init(uint16_t period_s) {
	if (timer16_initialized) return TIMER_INIT_ERROR;

	timer16_period = period_s - 1;

	ATOMIC_BLOCK(ATOMIC_FORCEON) {
		timer16_flag = false;

		TCCR1B |= (1 << WGM12); 
		// Count clock ticks to 1 second.
		OCR1A = 15625;
		TIMSK1 |= (1 << OCIE1A); 
	}

	timer16_initialized = 1;

	return TIMER_INIT_SUCCESS;
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

void timer16_deinit(void) {
	timer16_stop();
	timer16_initialized = 0;
}

ISR(TIMER1_COMPA_vect) {
	if (timer16_cycle_count < timer16_period) {
		++timer16_cycle_count;
	} else {
		timer16_flag += ((timer16_flag + 1) != 0);
		timer16_cycle_count = 0;
	}
}
