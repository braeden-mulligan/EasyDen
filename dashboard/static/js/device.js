class SH_Device {
	static SH_TYPE_NULL = 0;
	static SH_TYPE_RESERVED_1 = 1;
	static SH_TYPE_RESERVED_2 = 2;
	static SH_TYPE_RESERVED_3 = 3;
	static SH_TYPE_RESERVED_4 = 4;
	static SH_TYPE_RESERVED_5 = 5;
	static SH_TYPE_IRRIGATION = 6;
	static SH_TYPE_POWEROUTLET = 7;
	static SH_TYPE_THERMOSTAT = 8;
	static SH_TYPE_CAMERA = 9;

	static elem_tag_id = "div";
	static elem_tag_name = "div";
	static elem_tag_online = "div";
		
	static class_label_id = "sh-device-attr-id";
	static class_label_name = "sh-device-attr-name";
	static class_label_online = "sh-device-attr-online";

	schedules = [];

	constructor(type, id, name, online) {
		this.type = type;
		this.id = id;
		this.name = name;
		this.online = online;
	}

	differ(sh_device) {
		if (sh_device.type != this.type) return true;
		if (sh_device.id != this.id) return true;
		if (sh_device.name != this.name) return true;
		if (sh_device.online != this.online) return true;

		return false;
	}

	write_html() {
//TODO: pending update flag, states: inactive, loading, failed.

		var device_elem = document.createElement("div");
		device_elem.setAttribute("id", "device-" + this.id.toString());
		device_elem.setAttribute("class", "sh-device"); 

		var attr = document.createElement(SH_Device.elem_tag_id);
		attr.innerHTML = this.id.toString();
		attr.setAttribute("class", SH_Device.class_label_id);
		device_elem.append(attr);

		attr = document.createElement(SH_Device.elem_tag_name);
		attr.innerHTML = this.name.toString();
		attr.setAttribute("class", SH_Device.class_label_name); 
		device_elem.append(attr);

		attr = document.createElement(SH_Device.elem_tag_online);
		attr.innerHTML = this.online.toString();
		attr.setAttribute("class", SH_Device.class_label_online); 
		device_elem.append(attr);

		return device_elem;
	}
}

class Data_Tracker {
	global_poll = null;

	devices = [];
	devices_updated = [];

	pending_requests = [];
	pending_request_obj = {
		//device_id;
		//timeout_handle;
		//interval_handle;
	};

	ajax_response_processor = function(device_json) {
		// update devices after list;

		console.log(device_json);
	}

/*
	onTimeout(id)
		if pending(id)
		clear interval for id
			set device[id].html_write pending flag failed if interval running.

		clear timeout for if
	}

	onInterval(id) {
		if pending(id) check devices after list
			do device diff
			if diff, clear pending and set html pending flag inactive
				set devices before = devices_updated.
	}
*/

	submit_tracking = function (id = 0, command = "set", notify_callback = null) {
		/*
		setTimeout(function() {
			if (notify_callback) notify_callback();
		}, 3000);
		*/
/*
		device.write_html(pending_flag)

		id = id
		handle setInterval(watch device with id)
		handle setTimeout(on device id, notify_callback if not null, 5000);

		pending_requests append(handles)
*/
	}

	start_global_poll = function() {
		if (this.global_poll) return;

		fetch_devices(this.ajax_response_processor);
		this.global_poll = setInterval(function() {
			fetch_devices(this.ajax_response_processor);
		}.bind(this), 30000);
	}

	stop_global_poll = function() {
		if (this.global_poll) clearInterval(this.global_poll);
		this.global_poll = null;
	}

	constructor(response_processor) {
		if (response_processor) this.ajax_response_processor = response_processor;
		//this.start_global_poll();
	}
}

function fetch_devices(response_processor, id = 0, type = SH_Device.SH_TYPE_NULL) {
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
			devices = JSON.parse(xhr.responseText);
			response_processor(devices);
		}
	}

	xhr.open("GET", url, true);
	xhr.send();
}
