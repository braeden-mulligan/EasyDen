/*
 * Author: Braeden Mulligan
 *         braeden.mulligan@gmail.com
 *
 * Copyright: GNU GPL Version 3
 *
 */
#include <stdbool.h>
#include <stdint.h>

#ifndef AVR_TIMER_UTIL_H
#define AVR_TIMER_UTIL_H

volatile bool timer8_flag;

void timer8_init(uint16_t period_ms);

void timer8_start(void);

void timer8_stop(void);

void timer8_reset(void);


volatile bool timer16_flag;

void timer16_init(uint16_t period_s);

void timer16_start(void);

void timer16_stop(void);

void timer16_reset(void);

#endif
