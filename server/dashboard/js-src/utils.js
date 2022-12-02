function deep_copy(obj) {
	return JSON.parse(JSON.stringify(obj));
}

function sleep(milliseconds) {
  var start = new Date().getTime();
  for (var i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds){
      break;
    }
  }
}

/*
	{
		"recurring": bool,
		"time": "cron"/timestamp,
		"action": add/delete,
		"register": data
	}
*/
function build_schedule(register, data, action, recurring, time_expression) {
	let schedule_data = {
		register: register,
		data: data,
		action: action,
		recurring: recurring,
		time: time_expression
	}

	return JSON.stringify(schedule_data)
}

