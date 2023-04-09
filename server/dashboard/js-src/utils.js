function deep_copy(obj) {
	return JSON.parse(JSON.stringify(obj));
}

function obj_equals(obj_1, obj_2) {
	function is_object(obj) {
  		return obj != null && typeof obj === 'object';
	}
	const keys_1 = Object.keys(obj_1);
	const keys_2 = Object.keys(obj_2);
	if (keys_1.length !== keys_2.length) return false;

	for (const key of keys_1) {
		const val_1 = obj_1[key];
		const val_2 = obj_2[key];
		const areObjects = is_object(val_1) && is_object(val_2);

		if (areObjects && !obj_equals(val_1, val_2) || !areObjects && val_1 !== val_2) {
			return false;
		}
	}
	return true;
}

function build_request(data_handler) {
	try {
		var xhr = new XMLHttpRequest();
	} catch (e) {
		alert("Something went wrong!");
		return false;
	}

	xhr.onreadystatechange = function() {
		if (xhr.readyState == XMLHttpRequest.DONE) {
			console.log("Raw response:");
			console.log(xhr.responseText);
			data = JSON.parse(xhr.responseText);
			data_handler(data);
		}
	}

	return xhr;
}

function build_schedule(register, data, schedule_params, action = "create", id = null) {
	let schedule_data = {
		action: action
	};

	if (action == "delete") {
		if (id == null) alert("Problem needs debugging");
		schedule_data.id = id;

	} else if (action == "edit") {
		alert("Schedule edit unimplemented")

	} else if (action = "create") {
		if (schedule_params.time == null) alert("Problem needs debugging");

		time_data = { 
		  hour: schedule_params.time.split(":")[0], 
		  minute: schedule_params.time.split(":")[1], 
		  days: schedule_params.days || ""
		}

		schedule_data = {
			...schedule_data,
			register: register,
			attribute_data: data,
			time: time_data,
			recurring: (schedule_params.recurring == null) ? true : schedule_params.recurring,
			pause: schedule_params.pause ? schedule_params.pause : 0
		}
	}

	return JSON.stringify(schedule_data)
}

