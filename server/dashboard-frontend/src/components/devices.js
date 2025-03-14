import { useRef, useState } from "react";
import { add_schedule, remove_schedule, send_command } from "../api";

const InfoPane = function({ device }) {
	return (
	<div>
		<p>ID: { device.id } </p>
		<p>Name: { device.name }</p>
		<p>Online: { device.online.toString() }</p>
		{/* <p>Device enabled: { attributes.enabled.value } &nbsp;
			<button className="set" onClick={ () => update_attribute(attributes.enabled.register, + !attributes.enabled.value) } > Toggle </button>
		</p> */}
	</div>
	)
}

function MutableAttribute({ description, attribute, set_attribute }) {
	const current_target = useRef(null);
	console.log("mutable attr", attribute);

	return (
		<p>
			<span>{ description }: { attribute.value } &nbsp;
				<input type="text" onChange={ 
					(e) => { current_target.current = e.target.value; }
				} /> 
				<button className="set" onClick={
					() => {
						console.log(current_target.current)
						set_attribute(attribute.id, current_target.current)
					}
				}> 
					Set
				</button>
			</span>
		</p>
	);
}

function ScheduleTimeSelector({ schedule_data, on_update_schedule }) {
	const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
	const [selected_days, set_selected_days] = useState(days.map(() => false))

	function days_to_string(selected_days) {
		return days.filter((_, i) => selected_days[i]).map(day => day.toLowerCase()).join(",")
	}

	function handle_day_change(day_index, value) {
		const new_days = selected_days.slice(); 
		new_days[day_index] = value;

		const new_schedule_time = {...schedule_data.time}
		new_schedule_time.days = days_to_string(new_days);
		on_update_schedule({time: new_schedule_time})

 		set_selected_days(new_days);
	}

	return(<>
		<input type={"time"} onChange={(e) => {
			const new_schedule_time = {...schedule_data.time};
			const [hour, minute] = e.target.value.split(":");
			new_schedule_time.hour = hour;
			new_schedule_time.minute = minute;
			on_update_schedule({ time: new_schedule_time})
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
	</>)
}







 function ThermostatSchedules({ device }) {
	const [target_temperature, set_target_temperature] = useState(device.attributes.target_temperature.value);

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
			<div><span>Target temperature: &nbsp;
				<input type="range" min="10" max="30" step="0.25" value={target_temperature} onChange={ 
					(e) => {
						set_target_temperature(e.target.value)
					}
				} />
				<label>{ target_temperature }</label>
				<br />
			<ScheduleTimeSelector 
				schedule_data={new_schedule_data}
				on_update_schedule={(updated_data) => set_new_schedule_data((prev) => ({...prev, ...updated_data}))}
			/>
			<button className="set" onClick={() => {
				add_schedule(device, {
					...new_schedule_data,
					command: {
						"attribute-id": device.attributes.target_temperature.id,
						"attribute-value": target_temperature
					}
				})
			}}> Add 
			</button>
			</span></div>	
		</div>	
	);
}

export const Thermostat = function({ device }) {

	const set_attribute = function(attribute_id, value) {
		const command = {
			"attribute-id": attribute_id,
			"attribute-value": value 
		}

		send_command(device, command);
	}

	return (<>
		<p>THERMOSTAT</p>
		<InfoPane device={device} />
		<p>Temperature: { device.attributes.temperature.value.toFixed(1) + " °C" }</p>
		<MutableAttribute description="Target Temperature" attribute={device.attributes.target_temperature} set_attribute={set_attribute}/>
		{/* <Mutable_Attribute description="Temperature correction" attribute={ attributes.temperature_correction } update_attribute={ update_attribute } />
		<Mutable_Attribute description="Threshold high" attribute={ attributes.threshold_high } update_attribute={ update_attribute } />
		<Mutable_Attribute description="Threshold low" attribute={ attributes.threshold_low } update_attribute={ update_attribute } />
		<Mutable_Attribute description="Max heat time" attribute={ attributes.max_heat_time } update_attribute={ update_attribute } />
		<Mutable_Attribute description="Min cooldown time" attribute={ attributes.min_cooldown_time } update_attribute={ update_attribute } />
		<p>{JSON.stringify(device)}</p> */}
		<ThermostatSchedules device={device} />
	</>)
}










function PoweroutletSchedules({ device }) {
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

export const Poweroutlet = function({ device }) {
	function render_socket_states() {
		return device.attributes.socket_states.value.map((val, i) => {
			return(
			<li key={i}>
				<span socket_id={i}>Socket {i}: {val ? "ON" : "OFF"} &nbsp; </span>
				<button className="set" onClick={
					() => {
						let socket_states = device.attributes.socket_states.value.slice();
						socket_states[i] = + !socket_states[i];
						// set_attribute(attributes.socket_states., socket_states)
						send_command(device, {
							"attribute-id": device.attributes.socket_states.id,
							"attribute-value": socket_states
						})
					}
				} > Toggle </button>
			</li>
			);
		});
	}

	return (<>
		<p>POWEROUTLET</p>
		<InfoPane device={device} />
		<ul>
			{ render_socket_states() }
		</ul>
		<br/>
		<PoweroutletSchedules device={device} />
	</>)
}
