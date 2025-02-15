#include "avr_utilities.h"
#include "application_utilities.h"
#include "nano_configs_eeprom_offsets.h"

#include <avr/io.h>
#include <stdint.h>
#include <util/delay.h>
#include <avr/eeprom.h>

void nano_onboard_led_blink(int16_t count, uint16_t period_ms) {
	uint8_t ddrb_tmp = DDRB;
	uint8_t portb_tmp = PORTB;

	DDRB |= (1 << PB5);

	uint8_t infinite = 0;

	if (count < 0) {
		count = 1;
		infinite = 1;
	}

	for (uint16_t i = 0; (i < count) || infinite; ++i) {
		PORTB |= (1 << PB5);
		for (uint16_t j = 0; j < period_ms / 2; ++j) _delay_ms(1);

		PORTB &= ~(1 << PB5);
		for (uint16_t j = 0; j < period_ms / 2; ++j) _delay_ms(1);
	}

	PORTB = portb_tmp;
	DDRB = ddrb_tmp;
}

void load_metadata(struct device_metadata_t* md) {
	for (uint8_t i = 0; !eeprom_is_ready(); ++i) {
		_delay_ms(100);
		if (i > 10) nano_onboard_led_blink(-1, 1000);
	}
	md->type = eeprom_read_byte((uint8_t*)GENERIC_EEPROM_ADDR_TYPE);
	md->id = eeprom_read_byte((uint8_t*)GENERIC_EEPROM_ADDR_ID);
}