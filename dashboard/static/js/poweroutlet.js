// TODO: unhardcode this stuff
let server_addr = "192.168.1.79";

class Poweroutlet extends SH_Device {
	static get_count() {
		return this.format_message(this.CMD_GET, this.POWEROUTLET_REG_OUTLET_COUNT, 0);
	}

	static get_state() {
		return this.format_message(this.CMD_SET, this.POWEROUTLET_REG_STATE, 0);
	}

	// pass a list of tuples (<outlet index>, <boolean value>)
	static set_state(outlet_values) {
		var high_byte = 0;
		var low_byte = 0;

		for (var i = 0; i < outlet_values.length; ++i) {
			var [index, val] = outlet_values[i];

			high_byte |= (1 << index);
			if (val) low_byte |= (1 << index);
		}

		var reg_value = high_byte << 8 | low_byte;

		return this.format_message(this.CMD_SET, this.POWEROUTLET_REG_STATE, reg_value);
	}

	// return list of tuples (<outlet index>, <boolean value>)
	static parse_state(reg_value, outlet_count = 8) {
		if (outlet_count > 8) {
			console.log("WARNING: poweroutlet_read_state invalid argument passed.");
			outlet_count = 8;
		}

		if (typeof(reg_value) === "string") {
			reg_value = parseInt(reg_value, 16);
		} else if (typeof(reg_value !== "number")) {
			console.log("WARNING: in parse_state(), invalid reg_value");
		}
	
		var outlet_values = [];

		for (var i = 0; i < outlet_count; ++i) {
			if (reg_value & (1 << i)) {
				outlet_values.push([i, true]);
			} else {
				outlet_values.push([i, false]);
			}
		}

		return outlet_values;
	}
	
	constructor(id, name, online, registers) {
		SH_Device.POWEROUTLET_REG_STATE = 101;
		SH_Device.POWEROUTLET_REG_OUTLET_COUNT = 102;
		super(SH_Device.SH_TYPE_POWEROUTLET, id, name, online, registers);
	}
}

device = new Poweroutlet(0, "None", false, {});

var state_cmd = Poweroutlet.set_state([[0,1],[2,1],[1,0],[3,0]]);
console.log(state_cmd);
console.log(Poweroutlet.parse_state(state_cmd.split(',')[2]));


function refresh_devices() {
	console.log("fetching devices");

	var url = "http://" + server_addr + "/device/refresh?category=type&selector=" + SH_Device.SH_TYPE_POWEROUTLET.toString();

	try {
		var xhr = new XMLHttpRequest();
	} catch (e) {
		alert("Something went wrong!");
		return false;
	}

	xhr.onreadystatechange = function() {
	if (xhr.readyState == XMLHttpRequest.DONE) {
		console.log(xhr.responseText);
		poweroutlets = JSON.parse(xhr.responseText);
		}
	}

	xhr.open("GET", url, true);
	xhr.send();
}

function display_device(device_obj) {
	//get by id device panel
	//id, type, state register
}
