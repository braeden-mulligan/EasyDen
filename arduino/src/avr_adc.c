#include "avr_adc.h"

#include <avr/io.h>
#include <stdint.h>

void ADC_init(uint8_t DIDR0_pin_mask) {
    ADMUX = (1 << REFS0);
    ADCSRA = (1 << ADEN);
    ADCSRA |= (1 << ADPS0) | (1 << ADPS1) | (1 << ADPS2);
    DIDR0 = DIDR0_pin_mask;
}

static uint16_t ADC_convert(void) {
    ADCSRA |= (1 << ADSC);
    while (ADCSRA & (1 << ADSC)) { };

    return (ADC);
}

uint16_t ADC_read(uint8_t pin_Ax) {
	ADMUX &= ~(0xF);

	switch (pin_Ax) {
	case 0:
		break;
	case 1:
		ADMUX |= (1 << MUX0);
		break;
	case 2:
		ADMUX |= (1 << MUX1);
		break;
	case 3:
		ADMUX |= (1 << MUX0) | (1 << MUX1);
		break;
	case 4:
		ADMUX |= (1 << MUX2); 
		break;
	case 5:
		ADMUX |= (1 << MUX0) | (1 << MUX2);
		break;
	case 6:
		ADMUX |= (1 << MUX1) | (1 << MUX2);
		break;
	case 7:
		ADMUX |= (1 << MUX0) | (1 << MUX1) | (1 << MUX2);
		break;
	default:
		break;
	}

    return ADC_convert();
}

uint16_t ADC_onboard_temp() {
	ADMUX &= ~(0xF);
    ADMUX |= (1 << MUX3);

    return ADC_convert();
}

