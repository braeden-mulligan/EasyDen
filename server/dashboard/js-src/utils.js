function deep_copy(obj) {
	return JSON.parse(JSON.stringify(obj));
}

function build_schedule(register, data, action, recurring, time_expression) {
	let schedule_data = {
		register: register,
		attribute_data: data,
		action: action,
		recurring: recurring,
		time: time_expression,
		//pause: 0
	}

	//schedule_data["time"]["days"] = "mon";

	return JSON.stringify(schedule_data)
}

