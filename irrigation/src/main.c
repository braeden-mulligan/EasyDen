#include "arduino_wifi_framework.h"
#include "device_definition.h"
#include "protocol.h"
#include "avr_utilities.h"

#include "irrigation.h"

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
		//TODO: run pump?
		//nano_onboard_led_blink(8, 300);
		restore_app_conf();
	}
}

uint32_t handle_server_get(uint16_t reg) {
	union {
		float f;
		uint32_t i;
	} value_conversion; 

	switch (reg) {

	case GENERIC_REG_ENABLE:
		return irrigation_enabled;

	case GENERIC_REG_APP_INTERVAL:
		return app_conf.application_interval;

	case IRRIGATION_REG_SENSOR_COUNT:
		return sensor_count;

	case IRRIGATION_REG_PLANT_ENABLE:
		return plant_enable_mask;

	case IRRIGATION_REG_MOISTURE_0:
		value_conversion.f = moisture[0];
		return value_conversion.i;
	case IRRIGATION_REG_MOISTURE_1:
		value_conversion.f = moisture[1];
		return value_conversion.i;
	case IRRIGATION_REG_MOISTURE_2:
		value_conversion.f = moisture[2];
		return value_conversion.i;

	case IRRIGATION_REG_TARGET_MOISTURE_0:
		value_conversion.f = target_moisture[0];
		return value_conversion.i;
	case IRRIGATION_REG_TARGET_MOISTURE_1:
		value_conversion.f = target_moisture[1];
		return value_conversion.i;
	case IRRIGATION_REG_TARGET_MOISTURE_2:
		value_conversion.f = target_moisture[2];
		return value_conversion.i;

	case IRRIGATION_REG_MOISTURE_LOW_0:
		value_conversion.f = moisture_low[0];
		return value_conversion.i;
	case IRRIGATION_REG_MOISTURE_LOW_1:
		value_conversion.f = moisture_low[1];
		return value_conversion.i;
	case IRRIGATION_REG_MOISTURE_LOW_2:
		value_conversion.f = moisture_low[2];
		return value_conversion.i;

	case IRRIGATION_REG_MOISTURE_LOW_DELAY_0:
		return moisture_low_delay[0];
	case IRRIGATION_REG_MOISTURE_LOW_DELAY_1:
		return moisture_low_delay[1];
	case IRRIGATION_REG_MOISTURE_LOW_DELAY_2:
		return moisture_low_delay[2];

	case IRRIGATION_REG_SENSOR_RAW_0:
		return sensor_raw[0];
	case IRRIGATION_REG_SENSOR_RAW_1:
		return sensor_raw[1];
	case IRRIGATION_REG_SENSOR_RAW_2:
		return sensor_raw[2];

	case IRRIGATION_REG_SENSOR_RAW_MAX_0:
		return sensor_raw_max[0];
	case IRRIGATION_REG_SENSOR_RAW_MAX_1:
		return sensor_raw_max[1];
	case IRRIGATION_REG_SENSOR_RAW_MAX_2:
		return sensor_raw_max[2];

	case IRRIGATION_REG_SENSOR_RAW_MIN_0:
		return sensor_raw_min[0];
	case IRRIGATION_REG_SENSOR_RAW_MIN_1:
		return sensor_raw_min[1];
	case IRRIGATION_REG_SENSOR_RAW_MIN_2:
		return sensor_raw_min[2];

	case IRRIGATION_REG_MOISTURE_CHANGE_HYSTERESIS_TIME:
		return moisture_change_hysteresis_time;

	case IRRIGATION_REG_MOISTURE_CHANGE_HYSTERESIS_AMOUNT:
		return moisture_change_hysteresis_amount;

	case IRRIGATION_REG_CALIBRATION_MODE:
		return calibration_mode;

// Debug
	case 200:
		break;
	case 201:
		return sensor_recorded_max[0];
	case 202:
		return sensor_recorded_max[1];
	case 203:
		return sensor_recorded_max[2];
	case 204:
		return sensor_recorded_min[0];
	case 205:
		return sensor_recorded_min[1];
	case 206:
		return sensor_recorded_min[2];
	}

	return 0;
}

uint32_t handle_server_set(uint16_t reg, uint32_t val) {
	union {
		float f;
		uint32_t i;
	} value_conversion = { .i = val }; 

	switch (reg) {
	case GENERIC_REG_BLINK:
		set_conf_fast_period();
		blink_trigger = 1;
		break;

	case GENERIC_REG_ENABLE:
		set_irrigation_enabled(val);
		return irrigation_enabled;

	case GENERIC_REG_APP_INTERVAL:
		app_conf.application_interval = val; // (val > 3) ? val : 3;
		wifi_framework_init(app_conf);
		return app_conf.application_interval;

	case GENERIC_REG_RESET_CONFIGS:
		reset_configurations(val);
		break;

	case IRRIGATION_REG_PLANT_ENABLE:
		set_plant_enable(val);
		return plant_enable_mask;

	case IRRIGATION_REG_TARGET_MOISTURE_0:
		set_target_moisture(0, value_conversion.f);
		value_conversion.f = target_moisture[0];
		return value_conversion.i;
	case IRRIGATION_REG_TARGET_MOISTURE_1:
		set_target_moisture(1, value_conversion.f);
		value_conversion.f = target_moisture[1];
		return value_conversion.i;
	case IRRIGATION_REG_TARGET_MOISTURE_2:
		set_target_moisture(2, value_conversion.f);
		value_conversion.f = target_moisture[2];
		return value_conversion.i;

	case IRRIGATION_REG_MOISTURE_LOW_0:
		set_moisture_low(0, value_conversion.f);
		value_conversion.f = moisture_low[0];		
		return value_conversion.i;
	case IRRIGATION_REG_MOISTURE_LOW_1:
		set_moisture_low(1, value_conversion.f);
		value_conversion.f = moisture_low[1];		
		return value_conversion.i;
	case IRRIGATION_REG_MOISTURE_LOW_2:
		set_moisture_low(2, value_conversion.f);
		value_conversion.f = moisture_low[2];		
		return value_conversion.i;

	case IRRIGATION_REG_MOISTURE_LOW_DELAY_0:
		set_moisture_low_delay(0, val);
		return moisture_low_delay[0];
	case IRRIGATION_REG_MOISTURE_LOW_DELAY_1:
		set_moisture_low_delay(1, val);
		return moisture_low_delay[1];
	case IRRIGATION_REG_MOISTURE_LOW_DELAY_2:
		set_moisture_low_delay(2, val);
		return moisture_low_delay[2];

	case IRRIGATION_REG_SENSOR_RAW_MAX_0:
		set_sensor_raw_max(0, val);
		return sensor_raw_max[0];
	case IRRIGATION_REG_SENSOR_RAW_MAX_1:
		set_sensor_raw_max(1, val);
		return sensor_raw_max[1];
	case IRRIGATION_REG_SENSOR_RAW_MAX_2:
		set_sensor_raw_max(2, val);
		return sensor_raw_max[2];

	case IRRIGATION_REG_SENSOR_RAW_MIN_0:
		set_sensor_raw_min(0, val);
		return sensor_raw_min[0];
	case IRRIGATION_REG_SENSOR_RAW_MIN_1:
		set_sensor_raw_min(1, val);
		return sensor_raw_min[1];
	case IRRIGATION_REG_SENSOR_RAW_MIN_2:
		set_sensor_raw_min(2, val);
		return sensor_raw_min[2];

	case IRRIGATION_REG_MOISTURE_CHANGE_HYSTERESIS_TIME:
		set_moisture_change_hysteresis_time(val);
		return moisture_change_hysteresis_time;

	case IRRIGATION_REG_MOISTURE_CHANGE_HYSTERESIS_AMOUNT:
		set_moisture_change_hysteresis_amount(val);
		return moisture_change_hysteresis_amount;

	case IRRIGATION_REG_CALIBRATION_MODE:
		set_calibration_mode((val & 0x000000FF), val >> 8);
		return calibration_mode;

	}

	return 0;
}

void main_loop(void) {
	blink_identify();
	irrigation_control();
}

int main(void) {
	blink_trigger = 0;

	app_conf = wifi_framework_config_create();

	app_conf.wifi_startup_timeout = 7;
	app_conf.connection_interval = 20;
	app_conf.application_interval = 7;
	app_conf.server_message_get_callback = handle_server_get;
	app_conf.server_message_set_callback = handle_server_set;
	app_conf.app_main_callback = main_loop;
	app_conf.app_init_callback = irrigation_init;

	wifi_framework_init(app_conf);

	wifi_framework_start();

	// If here is reached error occurred
	nano_onboard_led_blink(-1, 1000);
	
	return 0;
}
