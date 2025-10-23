export const ENTITY_TYPE_MAP = {
	6: "irrigation",
	7: "poweroutlet",
	8: "thermostat"
}
export const DEVICE_POLL_PERIOD_MS = 30000;
export const SERVER_ADDR = location.hostname;

export const COMMON_COMMANDS = {
	Blink: {
		"attribute-id": 0x0F,
		"attribute-value": 0
	}
}

export const z_indices = {
	overlay: 2000,
}