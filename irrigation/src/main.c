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
		float sensor;
		uint32_t reg;
	} value_conversion; 

	switch (reg) {

// Debug
	case 200:
		break;
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
		return irrigation_enabled;

	case GENERIC_REG_APP_INTERVAL:
		app_conf.application_interval = (val > 3) ? val : 3;
		wifi_framework_init(app_conf);
		return app_conf.application_interval;
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
	app_conf.application_interval = 15;
	app_conf.server_message_get_callback = handle_server_get;
	app_conf.server_message_set_callback = handle_server_set;
	app_conf.app_main_callback = main_loop;
	app_conf.app_init_callback = irrigation_init;
	
	irrigation_init();
	for (;;) {
		irrigation_control();
	}

	wifi_framework_init(app_conf);

	wifi_framework_start();

	// If here is reached error occurred
	nano_onboard_led_blink(-1, 1000);
	
	return 0;
}
