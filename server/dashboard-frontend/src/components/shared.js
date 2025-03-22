import { useState } from "react";
import DeviceUnknownIcon from "@mui/icons-material/DeviceUnknown";
import SettingsIcon from '@mui/icons-material/Settings';
import { ToggleSwitch } from "./toggle-switch/toggle-switch";
import { send_command } from "../api";

export const InfoPane = function({ device, Icon, status, limited }) {
	const [current_status, set_current_status] = useState(device.attributes.enabled.value);

	const toggle_status = async function(value) {
		const response = await send_command(device, {
			"attribute-id": device.attributes.enabled.id,
			"attribute-value": +value
		});

		if (response?.result) {
			set_current_status(response.result[0].attributes.enabled.value);
		}
	}

	return (<>
		<div className="flex-row" style={{
			height: "48px",
			justifyContent: "space-between",
			padding: "4px 8px"
		}}>
			{<Icon fontSize="large"/> || <DeviceUnknownIcon fontSize="large" />}
			<p>{device.name}</p>
			<SettingsIcon fontSize="large"/>
		</div>
		<hr/>
		<div className="flex-row" style={{
			height: "40px",
			width: "100%",
			justifyContent: "space-between"
		}}>
			<div style={{ flex: 1 }}/>
			<div className="flex-row">
				{device.online ? 
					<p style={{ color: "green"}}>Online</p> :
					<p style={{ color: "red" }}>Offline</p> 
				}
				<p>&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;</p>
				<p>{status ? status : device.attributes.enabled.value ? "Enabled" : "Disabled" }</p>
			</div>
			<div className="flex-row" style={{
				flex: 1,
				justifyContent: "flex-end",
			}}>
				<ToggleSwitch style={{ paddingRight: "12px" }} value={current_status} onChange={toggle_status} disabled={limited}/>
			</div>
		</div>
		<hr/>
	</>);
}

export const ScheduleTimeSelector = function({ schedule_data, on_update_schedule }) {
	const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
	const [selected_days, set_selected_days] = useState(days.map(() => false));

	function days_to_string(selected_days) {
		return days.filter((_, i) => selected_days[i]).map(day => day.toLowerCase()).join(",");
	}

	function handle_day_change(day_index, value) {
		const new_days = selected_days.slice(); 
		new_days[day_index] = value;

		const new_schedule_time = {...schedule_data.time};
		new_schedule_time.days = days_to_string(new_days);
		on_update_schedule({time: new_schedule_time});

 		set_selected_days(new_days);
	}

	return(<>
		<input type={"time"} onChange={(e) => {
			const new_schedule_time = {...schedule_data.time};
			const [hour, minute] = e.target.value.split(":");
			new_schedule_time.hour = hour;
			new_schedule_time.minute = minute;
			on_update_schedule({ time: new_schedule_time});
		}}/>
		{days.map((day, i) => (
			<div key={day}>
				<input type={"checkbox"} id={day} onChange={(e) => handle_day_change(i, e.target.checked)}/>
				<label>{day}</label>
			</div>
		))}
		<div>
			<input type={"checkbox"} id={"Recurring"} onChange={(e) => on_update_schedule({...schedule_data, recurring: !e.target.checked})}/>
			<label>One-time</label>
		</div>
	</>);
}


// SCHEDULES:

// example input: schedule_renderer(schedule) {
// 	switch (schedule.command) {}
// 		case "target_temperature":
// 			<p> { schedule.command.value } </p>
// 		case "other_operating_param":
// 			...
// 	}
// }

// example input: schedule_adder(generate_command) {
// 	selection: useState one of ["target_temperature", "other_operating_command"]
// input type=select
// 	switch (selection) {
// 		case "target_temperature":
// 			<TargetTemperatureSelector>
// 				onChange: generate_command(attribute_id, attr value)
// 			</TargetTemperatureSelector>
// 		case "other_operating_param":
// 			...
// 	}
// }

// const Schedules = function({device, schedule_renderer, schedule_adder }) {
// 	const [new_schedule_data, set_new_schedule_data] = useState({
// 		command: {},
// 		time: {},
// 		recurring: true,
// 		pause: 0
// 	});

// 	existing schedules
// 	for (sched of device.schedules)
// 		<container>
// 		<days sched.time.days /> 
// 		<time sched.time hour:minute />
// 			render_schedule_command_data();
// 		</container>
// 	else <div>None</div>

//	<add_new_button display_adder_container/>
// 	<continer>
// 		schedule_adder((attr_id, attr_name) => 
// 			set_new_schedule_data((prev) => prev.command = {
// 				"id":
// 				"val"
// 			})
// 	<TimeSelector>
// 	</continer>

// }
