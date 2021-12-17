// TODO: unhardcode this stuff
let server_addr = "192.168.1.69";

class Poweroutlet extends SH_Device {
	static elem_tag_socket_count = "div";

	static class_label_socket_count = "poweroutlet-attr-socket-count";
	static class_label_socket_list = "poweroutlet-attr-socket-list";
	static class_label_socket_item = "poweroutlet-attr-socket-item";
	static class_label_socket_state = "poweroutlet-attr-socket-state";

	constructor(id, name, online, socket_count = 0, socket_states = []) {
		super(SH_Device.SH_TYPE_POWEROUTLET, id, name, online);
		this.socket_count = socket_count;
		this.socket_states = [];
		for (var i = 0; i < socket_states.length; ++i) {
			this.socket_states.push(socket_states[i]);
		}
	}

	copy() {
		var copy_states = [];
		for (var i = 0; i < this.socket_states.length; ++i) {
			copy_states.push(this.socket_states[i]);
		}

		return new Poweroutlet(this.id, this.name, this.online, this.socket_count, copy_states);
	}

	differ(sh_device) {
		if (this.type != sh_device.type) return undefined;

		if (super.differ(sh_device)) return true;

		for (var i = 0; i < this.socket_states.length; ++i) {
			if (this.socket_states[i] != sh_device.socket_states[i]) return true;
		}

		return false;
	}

	write_html(loading_flag = null) {
		var device_elem = document.getElementById("device-" + this.id.toString());

		if (device_elem != null) {
			// Update all attributes that are mutable.
			var socket_list;

//TODO: Put block into generic function?
			for (var i = 0; i < device_elem.children.length; ++i) {
				var attr = device_elem.children[i];
				if (attr.className == SH_Device.class_label_name) {
					attr.innerHTML = this.name;

				} else if (attr.className == SH_Device.class_label_online) {
					attr.innerHTML = this.online.toString();

				} else if (attr.className == Poweroutlet.class_label_socket_list) {
					socket_list = attr;

//TODO Make this better.
				} else if (attr.className == "sh-device-waiting-flag") {
					if (loading_flag == "loading") {
						attr.style.display = "block";
						attr.innerHTML = "Loading...";
					} else if (loading_flag == "error") {
						attr.style.display = "block";
						attr.innerHTML = "Error communicating with device";
					} else {
						attr.style.display = "none";
					}	
				}
			}

			//each item should have a button and a state value
			for (var i = 0; i < socket_list.children.length; ++i) {
				var socket_item = socket_list.children[i];
				for (var j = 0; j < socket_item.children.length; ++j) {
					if (socket_item.children[j].className == Poweroutlet.class_label_socket_state) {
						socket_item.children[j].innerHTML = "Socket " + i + ": " + (this.socket_states[i] ? "ON" : "OFF");
					}
				}
			}
	
			return null;
		}

		device_elem = super.write_html();

		var p = document.createElement(Poweroutlet.elem_tag_socket_count);
		p.innerHTML = "Socket count: " + this.socket_count;
		device_elem.append(p);

		var outlet_list = document.createElement("ul");
		outlet_list.setAttribute("class", Poweroutlet.class_label_socket_list);
		for (var i = 0; i < this.socket_states.length; ++i) {
			var entry = document.createElement("li");
			entry.setAttribute("class", Poweroutlet.class_label_socket_item);

			var outlet_state = document.createElement("p");
			outlet_state.setAttribute("class", Poweroutlet.class_label_socket_state);
			outlet_state.innerHTML = "Socket " + i + ": " + (this.socket_states[i] ? "ON" : "OFF");

			var toggle_button =  document.createElement("button");
			toggle_button.innerHTML = "Toggle";
			toggle_button.device_id = this.id;
			toggle_button.socket_index = i;
			toggle_button.addEventListener('click', toggle_action, false);

			entry.append(outlet_state);
			entry.append(toggle_button);

			outlet_list.append(entry);
		}

		device_elem.append(outlet_list);

console.log(device_elem);
		return device_elem;
	}
}

class Poweroutlet_Tracker extends Data_Tracker {
	constructor() {
		super(SH_Device.SH_TYPE_POWEROUTLET);
	}

	request_response_processor = function(device_json, tracking_object, device_id) {
	console.log("Request response");
		for (var i = 0; i < device_json.length; ++i) {
			var d = device_json[i];
			
	console.log("Received :");
			console.log(d);

			var poweroutlet = new Poweroutlet(d.id, d.name, d.online, d.socket_states.length, []);
			for (var i = 0; i < d.socket_states.length; ++i) {
				poweroutlet.socket_states.push(d.socket_states[i]);
			}

			var entry = tracking_object.device_entry(device_id);
			if (entry) {
	console.log("Existing :");
	console.log(tracking_object.devices_updated[entry.index]);

				tracking_object.devices_updated[entry.index] = poweroutlet;

	console.log("Updated :");
	console.log(tracking_object.devices_updated[entry.index]);
			} else {
				alert("Error: device mismatch. Contact Brad.");
			}
		}
	}

//TODO: Move to generic. Parse and pass specific device 
	global_poll_response_processor = function(device_json, tracking_object) {
		for (var i = 0; i < device_json.length; ++i) {
			var d = device_json[i];
//console.log(JSON.stringify(device_json[i]));

			var poweroutlet = new Poweroutlet(d.id, d.name, d.online, d.socket_states.length, d.socket_states);
			var entry = tracking_object.device_entry(d.id);

			if (entry) {
				tracking_object.devices_updated[entry.index] = poweroutlet;

				if (tracking_object.devices[entry.index].differ(poweroutlet)) {
					console.log("Global poll found diff");
					tracking_object.devices_updated[entry.index].write_html();
				}
				tracking_object.devices[i] = tracking_object.devices_updated[i].copy();

			} else {
		console.log("Adding new device");
				append_device_node(poweroutlet.write_html());
				tracking_object.device_add(poweroutlet);
			}
		}
	}
}

function append_device_node(node) {
	const device_panel = document.getElementById("device-panel");
	device_panel.append(node);
	device_panel.append(document.createElement("br"));
}

function notify(generic_param = null) {
	console.log("got notified");
}

tracker = new Poweroutlet_Tracker();

//TODO: This is debug only
function toggle_action(evt) {
	outlet_data = tracker.device_entry(evt.target.device_id).device.socket_states.slice();
	outlet_data[evt.target.socket_index] = +(!outlet_data[evt.target.socket_index]);
	send_command(evt.target.device_id, outlet_data);
	//tracker.submit_tracking(evt.target.device_id);
}

function send_command(id, command) {
//	tracker.stop_global_poll();

	console.log("Sending...");
	console.log(command);
	var url = "http://" + server_addr + "/device/command?id=" + id;

	try {
		var xhr = new XMLHttpRequest();
	} catch (e) {
		alert("Something went wrong!");
		return false;
	}

	xhr.onreadystatechange = function() {
		if (xhr.readyState == XMLHttpRequest.DONE) {
			console.log(xhr.responseText);
		}
	}

	xhr.open("POST", url, true);
	xhr.send(command);
}

// Main ----
/*
tracker.device_add(new Poweroutlet(69, "Nice device", false, 2, [1, 1]));
tracker.device_add(new Poweroutlet(420, "Dank device", false, 3, [1, 0, 1]));

for (var i = 0; i < tracker.devices.length; ++i) {
	append_device_node(device_node = tracker.devices[i].write_html());
}

var copy_outlet = tracker.devices[0].copy();
console.log("Orig:");
console.log(JSON.stringify(tracker.devices[0]));
console.log("Copy:");
console.log(JSON.stringify(copy_outlet));

copy_outlet.socket_states[0] = 0;

console.log("Orig update:");
console.log(JSON.stringify(tracker.devices[0]));
console.log("Copy update:");
console.log(JSON.stringify(copy_outlet));
*/

tracker.start_global_poll(true, 7000);
//tracker.submit_tracking(69, notify);

/*
setTimeout(function() {
	//tracker.devices_updated[0].online = true;
	tracker.devices_updated[0].socket_states[0] = 0;
}, 4700);
*/
