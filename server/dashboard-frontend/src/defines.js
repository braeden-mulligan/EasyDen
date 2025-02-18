export const DEVICE_TYPE_MAP = {
	6: "irrigation",
	7: "poweroutlet",
	8: "thermostat"
}

export const SERVER_ADDR = location.hostname;
export const ENVIRONMENT = (SERVER_ADDR == "192.168.1.69") ? "production" : "development";