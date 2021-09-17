//#include "ESP8266_link.h"
#include "arduino_wifi_app.h"
//#include "avr_timer_util.h"
//#include "avr_utilities.h"

#include <stdio.h>
#include <string.h>
#include <util/delay.h>

#define SERVER_MSG_SIZE_MAX 32

char server_message[SERVER_MSG_SIZE_MAX];

void handle_server_message(void) {

}

int main(void) {

	struct wifi_app_config app_conf = wifi_app_config_create();

	app_conf.wifi_startup_timeout = 10;
	app_conf.module_check_interval = 60;
	app_conf.server_buf_size = SERVER_MSG_SIZE_MAX;
	app_conf.server_message_buf = server_message;
	app_conf.server_message_callback = handle_server_message;
	app_conf.app_main_callback = NULL;
	
	wifi_app_init(&app_conf);

	wifi_app_start();

	/*
	//module_startup_procedure();
	uint16_t debug_count = 0;

	timer16_init(5);
	timer16_start();

	for (ever) {
	
		if (timer16_flag) {
				sprintf(debug_msg, "Sameple message #%d\r\n", debug_count);
				ESP8266_socket_send(&esp_params, 3000, debug_msg, strlen(debug_msg));
				++debug_count;
			}

			timer16_reset();
		}
	}
*/

	return 0;
}
