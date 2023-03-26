
function Thermostat_Attributes({ attributes, update_attribute }) {
	return (
	<div>
		<p>Device enabled: { attributes.enabled.value } &nbsp;
			<button className="set" onClick={
				() => update_attribute(attributes.enabled.register, + !attributes.enabled.value)
			} > Toggle </button>
		</p>
		<p>Temperature: { attributes.temperature.value.toFixed(1) + " °C" }</p>
		<Mutable_Attribute description="Target Temperature" attribute={ attributes.target_temperature } update_attribute={ update_attribute } />
		<Mutable_Attribute description="Temperature correction" attribute={ attributes.temperature_correction } update_attribute={ update_attribute } />
		<Mutable_Attribute description="Threshold high" attribute={ attributes.threshold_high } update_attribute={ update_attribute } />
		<Mutable_Attribute description="Threshold low" attribute={ attributes.threshold_low } update_attribute={ update_attribute } />
		<Mutable_Attribute description="Max heat time" attribute={ attributes.max_heat_time } update_attribute={ update_attribute } />
		<Mutable_Attribute description="Min cooldown time" attribute={ attributes.min_cooldown_time } update_attribute={ update_attribute } />
	</div>
	)
}

 function Thermostat_Schedules({ attributes, schedules, submit_schedule }) {
	[schedule_data, set_schedule_data] = useState({
		time: "",
		days: "",
	});

	[target_temperature, set_target_temperature] = useState(attributes.target_temperature.value);

	function add_schedule() {
		let new_schedule = build_schedule(
		  attributes.target_temperature.register,
		  target_temperature, 
		  schedule_data
		)
		submit_schedule(new_schedule);
	}

	function remove_schedule(id) {
		submit_schedule(build_schedule(null, null, null, "delete", null, null, id))
	}

	function render_schedule(obj) {
		return (
		<li key={ JSON.stringify(obj.id)}> { JSON.stringify(obj) }
			<button className="set" onClick={ () => remove_schedule(obj.id) } > Remove </button>
		</li>
		)
	}

	let rendered_schedules = schedules.map((obj, i) => {
		return render_schedule(obj, i)
	})

	if (!rendered_schedules.length) {
		rendered_schedules = <p>None</p>;
	}

	function on_update_schedule(updated_time = null, updated_days = null) {
		if (updated_time) set_schedule_data(prev => ({...prev, time: updated_time}));
		if (updated_days) set_schedule_data(prev => ({...prev, days: updated_days}));
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
			<input type="range" min="10" max="30" step="0.25" value={ target_temperature } onChange={ 
				(e) => { set_target_temperature(e.target.value) }
			} />
			<label>{ target_temperature }</label>
			<br />
		<Schedule_Time_Selector on_update_schedule={ on_update_schedule }/>
		<button className="set" onClick={ () => add_schedule() } > Add 
		</button>
		</span></div>	
		</div>	
	);
}