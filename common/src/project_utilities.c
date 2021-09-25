#include "project_utilities.h"
#include "device_definition.h"

#if defined (__AVR_ATmega328P__)
	#include "avr_utilities.h"

	#include <avr/eeprom.h>
	#include <util/delay.h>

	void load_metadata(struct sh_device_metadata* md) {
		for (uint8_t i = 0; !eeprom_is_ready(); ++i) {
			_delay_ms(100);
			if (i > 10) blink_led(-1, 1000);
		}
		md->type = eeprom_read_byte((uint8_t*)EEPROM_ADDR_TYPE);
		md->id = eeprom_read_byte((uint8_t*)EEPROM_ADDR_ID);
	}
#else
	void load_metadata(struct sh_metadata* md) { }
#endif
