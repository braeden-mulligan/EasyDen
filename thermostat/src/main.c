#include "arduino_wifi_framework.h"
#include "device_definition.h"
#include "protocol.h"
#include "avr_utilities.h"

#include "thermostat.h"

struct wifi_framework_config app_conf;
struct wifi_framework_config tmp_conf;

uint8_t blink_trigger;

void set_conf_fast_period(void) {
	tmp_conf = app_conf;
	tmp_conf.application_interval = 1;
	wifi_framework_init(tmp_conf);
}

void restore_app_conf(void) {
	wifi_framework_init(app_conf);
}

void blink_identify(void) {
	if (blink_trigger) {
		blink_trigger = 0;
		nano_onboard_led_blink(8, 300);
		restore_app_conf();
	}
}

uint32_t handle_server_get(uint16_t reg) {
	union {
		float sensor;
		uint32_t reg;
	} value_conversion; 

	switch (reg) {

	case THERMOSTAT_REG_TEMPERATURE:
		value_conversion.sensor = temperature;
		return value_conversion.reg;

	case THERMOSTAT_REG_HUMIDITY:
		value_conversion.sensor = humidity;
		return value_conversion.reg;

	case THERMOSTAT_REG_HUMIDITY_SENSOR_COUNT:
		return humidity_sensor_count;

	case GENERIC_REG_ENABLE:
		return thermostat_enabled;

	case GENERIC_REG_APP_INTERVAL:
		return app_conf.application_interval;

	case THERMOSTAT_REG_TARGET_TEMPERATURE:
		value_conversion.sensor = target_temperature;
		return value_conversion.reg;

	case THERMOSTAT_REG_TEMPERATURE_CORRECTION:
		value_conversion.sensor = temperature_correction;
		return value_conversion.reg;

	case THERMOSTAT_REG_THRESHOLD_HIGH:
		value_conversion.sensor = threshold_high;
		return value_conversion.reg;

	case THERMOSTAT_REG_THRESHOLD_LOW:
		value_conversion.sensor = threshold_low;
		return value_conversion.reg;

	case THERMOSTAT_REG_HUMIDITY_CORRECTION:
		value_conversion.sensor = humidity_correction;
		return value_conversion.reg;

	case THERMOSTAT_REG_MAX_HEAT_TIME:
		return max_heat_time;

	case THERMOSTAT_REG_MIN_COOLDOWN_TIME:
		return min_cooldown_time;

// Debug
	case 200:
		return thermostat_state();
	case 201:
		return heater_triggered_count;
	case 202: 
		return cooldown_triggered_count;
	case 203:
		return sensor_error_total;
	}

	return 0;
}

uint32_t handle_server_set(uint16_t reg, uint32_t val) {
	union {
		float sensor;
		uint32_t reg;
	} value_conversion = { .reg = val }; 

	switch (reg) {
	case GENERIC_REG_BLINK:
		set_conf_fast_period();
		blink_trigger = 1;
		break;

	case GENERIC_REG_ENABLE:
		set_thermostat_enabled(val);
		return thermostat_enabled;

	case GENERIC_REG_APP_INTERVAL:
		app_conf.application_interval = (val > 3) ? val : 3;
		wifi_framework_init(app_conf);
		return app_conf.application_interval;

	case THERMOSTAT_REG_TARGET_TEMPERATURE:
		set_target_temperature(value_conversion.sensor);
		return value_conversion.reg;

	case THERMOSTAT_REG_TEMPERATURE_CORRECTION:
		set_temperature_correction(value_conversion.sensor);
		return value_conversion.reg;

	case THERMOSTAT_REG_THRESHOLD_HIGH:
		set_threshold_high(value_conversion.sensor);
		return value_conversion.reg;

	case THERMOSTAT_REG_THRESHOLD_LOW:
		set_threshold_low(value_conversion.sensor);
		return value_conversion.reg;

	case THERMOSTAT_REG_HUMIDITY_CORRECTION:
		set_humidity_correction(value_conversion.sensor);
		return value_conversion.reg;

	case THERMOSTAT_REG_MAX_HEAT_TIME:
		set_max_heat_time(value_conversion.reg);
		return value_conversion.reg;

	case THERMOSTAT_REG_MIN_COOLDOWN_TIME:
		set_min_cooldown_time(value_conversion.reg);
		return value_conversion.reg;
	}

	return 0;
}

void main_loop(void) {
	blink_identify();
	thermostat_control();
}

int main(void) {
	blink_trigger = 0;

	app_conf = wifi_framework_config_create();

	app_conf.wifi_startup_timeout = 7;
	app_conf.connection_interval = 20;
	app_conf.application_interval = 15;
	app_conf.server_message_get_callback = handle_server_get;
	app_conf.server_message_set_callback = handle_server_set;
	app_conf.app_main_callback = main_loop;
	app_conf.app_init_callback = thermostat_init;
	
	wifi_framework_init(app_conf);

	wifi_framework_start();

	// If here is reached error occurred
	nano_onboard_led_blink(-1, 1000);
	
	return 0;
}
