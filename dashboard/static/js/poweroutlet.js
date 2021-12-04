// TODO: unhardcode this stuff
let server_addr = "192.168.1.79";

class Poweroutlet extends SH_Device {
	static elem_tag_socket_count = "div";

	static class_label_socket_count = "poweroutlet-attr-socket-count";
	static class_label_socket_list = "poweroutlet-attr-socket-list";
	static class_label_socket_item = "poweroutlet-attr-socket-item";
	static class_label_socket_state = "poweroutlet-attr-socket-state";

	constructor(id, name, online, socket_count = 0, socket_states = []) {
		super(SH_Device.SH_TYPE_POWEROUTLET, id, name, online);
		this.socket_count = socket_count;
		this.socket_states = socket_states;
	}

	differ(sh_device) {
		return super.differ(sh_device);

		return false;
	}

	write_html() {
		var device_elem = document.getElementById("device-" + this.id.toString());

		if (device_elem != null) {
			// Update all attributes that are mutable.
			var socket_list;

//TODO: Put block into generic function
			for (var i = 0; i < device_elem.children.length; ++i) {
				var attr = device_elem.children[i];
				if (attr.className == SH_Device.class_label_name) {
					attr.innerHTML = this.name;

				} else if (attr.className == SH_Device.class_label_online) {
					attr.innerHTML = this.online.toString();

				} else if (attr.className == Poweroutlet.class_label_socket_list) {
					socket_list = attr;
				}
			}

			//each item should have a button and a pair/value
			for (var i = 0; i < socket_list.children.length; ++i) {
				var socket_item = socket_list.children[i];
				for (var j = 0; j < socket_item.children.length; ++j) {
					if (socket_item.children[j].className == Poweroutlet.class_label_socket_state) {
//TODO: properly associate object index with labeled index
						socket_item.children[j].innerHTML = "Socket " + this.socket_states[i][0] + ": " + (this.socket_states[i][1] ? "ON" : "OFF");
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

			var outlet_pair = document.createElement("p");
			outlet_pair.setAttribute("class", Poweroutlet.class_label_socket_state);
			outlet_pair.innerHTML = "Socket " + this.socket_states[i][0] + ": " + (this.socket_states[i][1] ? "ON" : "OFF");

			var toggle_button =  document.createElement("button");
			toggle_button.innerHTML = "Toggle";
			toggle_button.device_id = this.id;
			toggle_button.addEventListener('click', toggle_action, false);

			entry.append(outlet_pair);
			entry.append(toggle_button);

			outlet_list.append(entry);
		}

		device_elem.append(outlet_list);

		return device_elem;
	}
}

function notify(generic_param = null) {
	console.log("got notified");
}

data_tracker = new Data_Tracker();
data_tracker.start_global_poll();
data_tracker.submit_tracking(1, "set", notify);

function toggle_action(evt) {
	console.log("Clicked device " + evt.target.device_id);
	data_tracker.submit_tracking(evt.target.device_id);
}

// Test ----
devices = [];

devices.push(new Poweroutlet(69, "Nice device", false, 2, [[0,1],[1,1]]));
devices.push(new Poweroutlet(420, "Dank device", false, 3, [[0,1],[1,0],[2,1]]));

console.log("Diff check: " + devices[0].differ(devices[0]));

const device_panel = document.getElementById("device-panel");

for (var i = 0; i < devices.length; ++i) {
	device_node = devices[i].write_html();
	console.log(device_node);
	device_panel.append(device_node);
	device_panel.append(document.createElement("br"));
}

setTimeout(function() {
	console.log("Updated devices");
	devices[0].online = true;
	devices[0].socket_states[0][1] = false;
	devices[0].write_html();
}, 2000);



