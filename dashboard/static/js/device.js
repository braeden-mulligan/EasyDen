class SH_Device {
	static SH_TYPE_RESERVED_1 = 0;
	static SH_TYPE_RESERVED_2 = 1;
	static SH_TYPE_RESERVED_3 = 2;
	static SH_TYPE_RESERVED_4 = 3;
	static SH_TYPE_RESERVED_5 = 4;
	static SH_TYPE_CAMERA = 5;
	static SH_TYPE_IRRIGATION = 6;
	static SH_TYPE_POWEROUTLET = 7;
	static SH_TYPE_THERMOSTAT = 8;

	static GENERIC_REG_NULL = 0;
	static GENERIC_REG_RESERVED_1 = 1;
	static GENERIC_REG_RESERVED_2 = 2;
	static GENERIC_REG_RESERVED_3 = 3;
	static GENERIC_REG_RESERVED_4 = 4;
	static GENERIC_REG_RESERVED_5 = 5;
	static GENERIC_REG_ENABLE = 6;
	static GENERIC_REG_PING = 7;
	static GENERIC_REG_DATE = 9;
	static GENERIC_REG_TIME = 10;
	static GENERIC_REG_SCHEDULE = 12;
	static GENERIC_REG_SCHEDULE_ENABLE = 13;
	static GENERIC_REG_SCHEDULE_COUNT = 14;
	static GENERIC_REG_APP_FREQUENCY = 20;
	static GENERIC_REG_POLL_FREQUENCY = 21;
	static GENERIC_REG_PUSH_ENABLE = 31;
	static GENERIC_REG_PUSH_FREQUENCY = 32;
	static GENERIC_REG_PUSH_BUFFERING = 33;

	static CMD_NUL = 0;
	static CMD_GET = 1;
	static CMD_SET = 2;

	static format_message(cmd, reg, val) {
		var message = cmd.toString(16).toUpperCase().padStart(2, "0") + ",";
		message += reg.toString(16).toUpperCase().padStart(2, "0") + ",";
		message += val.toString(16).toUpperCase().padStart(8, "0");
		return message;
	}

	constructor(type, id, name, online, registers) {
		this.type = type;
		this.id = id;
		this.name = name;
		this.online = online
		this.registers = {}
	}
}
