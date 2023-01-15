#include "irrigation.h"

#include "avr_adc.h"
#include "avr_utilities.h"
#include "avr_timer_util.h"
#include "device_definition.h"
#include "nano_configs_eeprom_offsets.h"

#include <avr/eeprom.h>
#include <avr/io.h>
#include <util/delay.h>

#define MEM_ENABLE 512

enum {
	OFF = 0,
	ON
};

void set_irrigation_enabled(uint8_t value) {
}

void irrigation_init(void) {
	irrigation_enabled = eeprom_read_byte((uint8_t*)MEM_ENABLE);

	// Pump relay
	DDRD |= 1 << PD4;
	PORTD &= ~(1 << PD4);

	// Pot selection valve relays
	DDRD |= 1 << PD5;
	DDRD |= 1 << PD6;
	PORTD &= ~(1 << PD5);
	PORTD &= ~(1 << PD6);

	DDRB &= !(1 << PB0);
	DDRB &= !(1 << PB1);
	DDRB &= !(1 << PB2);
	
	PORTB |= 1 << PB0 | 1 << PB1 | 1 << PB2;
}

void system_error_lock(void) {
	nano_onboard_led_blink(-1, 1000);
}

void irrigation_control(void) {
	//nano_onboard_led_blink(4, 300);

	if (!(PINB & 1 << PB0)) {
		PORTD |= 1 << PD4;
	} else {
		PORTD &= ~(1 << PD4);
	}

	if (!(PINB & (1 << PB1))) {
		PORTD |= 1 << PD5;
	} else {
		PORTD &= ~(1 << PD5);
	}

	if (!(PINB & (1 << PB2))) {
		PORTD |= 1 << PD6;
	} else {
		PORTD &= ~(1 << PD6);
	}
}

uint8_t irrigation_state(void) {
	return 0;
}
