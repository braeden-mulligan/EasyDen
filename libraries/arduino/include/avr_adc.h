#include <stdint.h>

#ifndef AVR_ADC_H
#define AVR_ADC_H

void ADC_init(uint8_t DIDR0_pin_mask, uint8_t use_external_reference_voltage);

uint16_t ADC_read(uint8_t pin_Ax);

uint16_t ADC_onboard_temp(void);

#endif
