#ifndef SH_DEVICE_DEFINITION_H
#define SH_DEVICE_DEFINITION_H

#include <stdint.h>

struct sh_device_metadata {
	uint8_t type;
	uint8_t id;
};

/*
	Device type enumeration.
*/
#define SH_TYPE_NULL 0
#define SH_TYPE_RESERVED_1 1
#define SH_TYPE_RESERVED_2 2
#define SH_TYPE_RESERVED_3 3
#define SH_TYPE_RESERVED_4 4
#define SH_TYPE_RESERVED_5 5
#define SH_TYPE_IRRIGATION 6
#define SH_TYPE_POWEROUTLET 7
#define SH_TYPE_THERMOSTAT 8
#define SH_TYPE_CAMERA 9

/*
	Registers per device.
	All vlues are passed as integers but may not represent integers in device units.
*/
#define GENERIC_REG_NULL 0
#define GENERIC_REG_RESERVED_1 1
#define GENERIC_REG_RESERVED_2 2
#define GENERIC_REG_RESERVED_3 3
#define GENERIC_REG_RESERVED_4 4
#define GENERIC_REG_RESERVED_5 5
#define GENERIC_REG_ENABLE 6
#define GENERIC_REG_PING 7
//#define GENERIC_REG_KEEPALIVE 8
/*
#define GENERIC_REG_DATE 9
#define GENERIC_REG_TIME 10
#define GENERIC_REG_WEEKDAY 11 // Can fit in one byte of the date register
#define GENERIC_REG_SCHEDULE 12
#define GENERIC_REG_SCHEDULE_ENABLE 13
#define GENERIC_REG_SCHEDULE_COUNT 14
*/
#define GENERIC_REG_BLINK 19
#define GENERIC_REG_APP_INTERVAL 20
#define GENERIC_REG_POLL_INTERVAL 21
#define GENERIC_REG_PUSH_ENABLE 22
#define GENERIC_REG_PUSH_INTERVAL 23
#define GENERIC_REG_PUSH_BUFFERING 24

#define POWEROUTLET_REG_STATE 101
#define POWEROUTLET_REG_SOCKET_COUNT 102

#define THERMOSTAT_REG_TEMPERATURE 101
#define THERMOSTAT_REG_TARGET_TEMPERATURE 102
#define THERMOSTAT_REG_THRESHOLD_HIGH 103
#define THERMOSTAT_REG_THRESHOLD_LOW 104
//#define THERMOSTAT_REG_HYSTERESIS 105
#define THERMOSTAT_REG_MAX_HEAT_TIME 106
#define THERMOSTAT_REG_MIN_COOLDOWN_TIME 107
#define THERMOSTAT_REG_HUMIDITY 108
#define THERMOSTAT_REG_TEMPERATURE_CORRECTION 109
#define THERMOSTAT_REG_HUMIDITY_CORRECTION 110
#define THERMOSTAT_REG_THERMOMETER_COUNT 111
#define THERMOSTAT_REG_HUMIDITY_SENSOR_COUNT 112

#define IRRIGATION_REG_MOISTURE 101
#define IRRIGATION_REG_TARGET_MOISTURE 102
#define IRRIGATION_REG_THRESHOLD_HIGH 103
#define IRRIGATION_REG_THRESHOLD_LOW 104
#define IRRIGATION_REG_HYSTERESIS 105
#define IRRIGATION_REG_MIN_COOLDOWN 106
#define IRRIGATION_REG_SWITCH_COUNTER 107
#define IRRIGATION_REG_SENSOR_RAW 108
#define IRRIGATION_REG_SENSOR_RAW_MAX 109
#define IRRIGATION_REG_SENSOR_RAW_MIN 110
#define IRRIGATION_REG_SENSOR_COUNT 111
#define IRRIGATION_REG_SENSOR_MUX 112
#define IRRIGATION_REG_MOISTURE_LOW_DELAY 114

#endif