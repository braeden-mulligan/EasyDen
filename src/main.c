#include "avr_ESP8266_link.h"
#include "avr_utilities.h"
#include "util/delay.h"

int main(void) {
	ESP8266_link_init();

	_delay_ms(2000);

	if (ESP8266_ping(2000) == ESP8266_CMD_SUCCESS) blink_led(3, 500);

	return 0;
}
