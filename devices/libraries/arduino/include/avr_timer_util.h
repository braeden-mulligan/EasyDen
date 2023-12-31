/*
 * Author: Braeden Mulligan
 *         braeden.mulligan@gmail.com
 *
 * Copyright: GNU GPL Version 3
 *
 */
#include <stdint.h>

#ifndef AVR_TIMER_UTIL_H
#define AVR_TIMER_UTIL_H

volatile uint8_t timer8_flag;

uint8_t timer8_running;

void timer8_init(uint16_t period_ms, uint8_t low_res);

void timer8_start(void);

void timer8_stop(void);

void timer8_restart(void);


volatile uint16_t timer16_flag;

uint8_t timer16_running;

void timer16_init(uint16_t period_s);

void timer16_start(void);

void timer16_stop(void);

void timer16_restart(void);

void timer16_pause(void);

void timer16_resume(void);

#endif
