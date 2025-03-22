import { useState } from 'react';
import { InfoPane, MutableAttribute, ScheduleTimeSelector } from './shared'
import { add_schedule, remove_schedule, send_command } from "../api";
import DeviceThermostatIcon from "@mui/icons-material/DeviceThermostat";

export const ThermostatSchedules = function({ device }) {
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

export const Thermostat = function({ device, limited }) {
	const [target_temperature, set_target_temperature] = useState(device.attributes.target_temperature.value);

	const set_attribute = function(attribute_id, value) {
		const command = {
			"attribute-id": attribute_id,
			"attribute-value": value 
		}

		send_command(device, command);
	}

	const status = (() => {
		console.log(device.attributes.status?.value);
		switch(device.attributes.status?.value) {
			case 0:
				return "Disabled";
			case 1:
				return "Idle";
			case 2: 
				return "Heating 🔥";
			case 3:
				return "Forced idle";
		}

		return "Status unknown";
	})();

	return (<>
		<InfoPane device={device} Icon={DeviceThermostatIcon} status={status} limited={limited}/>
		<p>Temperature: { device.attributes.temperature.value.toFixed(1) + " °C" }</p>
		{!limited && <>
			<input type="range" min="10" max="30" step="0.25" style={{ writingMode: "vertical-lr", direction: "rtl" }} value={target_temperature} onChange={ 
				(e) => {
					set_target_temperature(e.target.value)
				}
			} />
			<label>{ target_temperature }</label>
			<br />
			<button className="set" onClick={
				() => set_attribute(device.attributes.target_temperature.id, target_temperature)
			}> 
				Set
			</button>
		</>}
		{/* <MutableAttribute description="Target Temperature" attribute={device.attributes.target_temperature} set_attribute={set_attribute}/> */}
		{/* <Mutable_Attribute description="Temperature correction" attribute={ attributes.temperature_correction } update_attribute={ update_attribute } />
		<Mutable_Attribute description="Threshold high" attribute={ attributes.threshold_high } update_attribute={ update_attribute } />
		<Mutable_Attribute description="Threshold low" attribute={ attributes.threshold_low } update_attribute={ update_attribute } />
		<Mutable_Attribute description="Max heat time" attribute={ attributes.max_heat_time } update_attribute={ update_attribute } />
		<Mutable_Attribute description="Min cooldown time" attribute={ attributes.min_cooldown_time } update_attribute={ update_attribute } />
		<p>{JSON.stringify(device)}</p> */}
		{!limited && <ThermostatSchedules device={device} />}
	</>)
}


