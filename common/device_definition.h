#ifndef SH_DEVICE_DEFINITION_H
#define SH_DEVICE_DEFINITION_H

#include <stdint.h>

#if defined (__AVR_ATmega328P__)
	#define EEPROM_ADDR_TYPE 8
	#define EEPROM_ADDR_ID 9
#endif

struct sh_device_metadata {
	uint8_t type;
	uint8_t id;
};

/*
	Device type enumeration.
*/
#define SH_RESERVED_1 0
#define SH_RESERVED_2 1
#define SH_RESERVED_3 2
#define SH_RESERVED_4 3
#define SH_RESERVED_5 4
#define SH_CAMERA 5
#define SH_IRRIGATION 6
#define SH_POWEROUTLET 7
#define SH_THERMOSTAT 8

/*
	Registers per device.
	All vlues are passed as integers but may not represent integers in device units.
*/
#define SMARTHOME_REG_NULL 0

#define IRRIGATION_REG_ENABLE 1
#define IRRIGATION_REG_POLL_FREQUENCY 2
#define IRRIGATION_REG_PUSH_ENABLE 3
#define IRRIGATION_REG_PUSH_FREQUENCY 4
#define IRRIGATION_REG_PUSH_BUFFERING 5
#define IRRIGATION_REG_MOISTURE 6
#define IRRIGATION_REG_TARGET_MOISTURE 7
#define IRRIGATION_REG_THRESHOLD_HIGH 8
#define IRRIGATION_REG_THRESHOLD_LOW 9
#define IRRIGATION_REG_HYSTERESIS 10
#define THERMOSTAT_REG_MIN_COOLDOWN 11
#define IRRIGATION_REG_SWITCH_COUNTER 12

#define POWEROUTLET_REG_ENABLE 1
#define POWEROUTLET_REG_PUSH_ENABLE 3
#define POWEROUTLET_REG_PUSH_FREQUENCY 4
#define POWEROUTLET_REG_PUSH_BUFFERING 5
#define POWEROUTLET_REG_STATE 6
#define POWEROUTLET_REG_OUTLET_COUNT 7

#define THERMOSTAT_REG_ENABLE 1
#define THERMOSTAT_REG_POLL_FREQUENCY 2
#define THERMOSTAT_REG_PUSH_ENABLE 3
#define THERMOSTAT_REG_PUSH_FREQUENCY 4
#define THERMOSTAT_REG_PUSH_BUFFERING 5
#define THERMOSTAT_REG_TEMPERATURE 6
#define THERMOSTAT_REG_TARGET_TEMPERATURE 7
#define THERMOSTAT_REG_THRESHOLD_HIGH 8
#define THERMOSTAT_REG_THRESHOLD_LOW 9
#define THERMOSTAT_REG_HYSTERESIS 10
#define THERMOSTAT_REG_MIN_COOLDOWN 11
#define THERMOSTAT_REG_HUMIDITY 12

#endif
