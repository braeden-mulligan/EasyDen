import { useState } from "react";
import { InfoPane, ScheduleTimeSelector } from './shared'
import { add_schedule, remove_schedule, send_command } from "../api";
import PowerIcon from "@mui/icons-material/Power";

export const PoweroutletSchedules = function({ device }) {
	const [target_settings, set_target_settings] = useState(Array(device.attributes.socket_count.value).fill(null));

	const [new_schedule_data, set_new_schedule_data] = useState({
		command: {},
		time: {},
		recurring: true,
		pause: 0
	});

	let rendered_schedules = device.schedules.map((schedule) => {
		return(
			<li key={ JSON.stringify(schedule.id)}> { JSON.stringify(schedule) }
				<button className="set" onClick={() => remove_schedule(device, schedule.id)}> Remove </button>
			</li>
		)
	})

	if (!rendered_schedules.length) {
		rendered_schedules = <p>None</p>;
	}

	return (
		<div>
			<b>Schedules</b>
			<ul>
				{ rendered_schedules }
			</ul>
			<br />
			<b>New Schedule</b>
			<div><span>
				Socket values&nbsp;
				{target_settings.map((_, index) => (
					<input key={index} type="number" min={-1} max={1} onChange={(e) => { 
						const target_states = target_settings.slice();
						target_states[index] = Number(e.target.value) > -1 ? !!Number(e.target.value) : null;
						set_target_settings(target_states) }}
					/>)
				)}
			</span></div>	
			<ScheduleTimeSelector 
				schedule_data={new_schedule_data}
				on_update_schedule={(updated_data) => set_new_schedule_data((prev) => ({...prev, ...updated_data}))}
			/>
			<button className="set" onClick={() => {
				add_schedule(device, {
					...new_schedule_data,
					command: {
						"attribute-id": device.attributes.socket_states.id,
						"attribute-value": target_settings
					}
				})
			}}> Add 
			</button>
		</div>	
	);
}

export const Poweroutlet = function({ device, limited }) {
	function render_socket_states() {
		return device.attributes.socket_states.value.map((val, i) => {
			return(
			<li key={i}>
				<span socket_id={i}>Socket {i}: {val ? "ON" : "OFF"} &nbsp; </span>
				<button className="set" disabled={limited} onClick={() => {
					const target_states = device.attributes.socket_states.value;
					target_states[i] = !target_states[i]
					send_command(device, {
						"attribute-id": device.attributes.socket_states.id,
						"attribute-value": target_states
					})}}
				>
					Toggle
				</button>
			</li>
			);
		});
	}

	return (<>
		<InfoPane device={device} Icon={PowerIcon} limited={limited} />
		<ul>
			{ render_socket_states() }
		</ul>
		<br/>
		{!limited && <PoweroutletSchedules device={device} />}
	</>)
}
