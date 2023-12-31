
function socket_option(index, on_update) {
	return <input key={index} type="number" min="-1" max="1" onChange={(e) => { on_update(index, e.target.value) }}/>
}

function Poweroutlet_Attributes({ attributes, update_attribute }) {
	function render_socket_states() {
		let rendered_sockets = attributes.socket_states.value.map((val, i) => {
			return(
			<li key={ i }>
				<span socket_id={i}>Socket {i}: {val ? "ON" : "OFF"} &nbsp; </span>
				<button className="set" onClick={
					() => {
						let socket_states = attributes.socket_states.value.slice();
						socket_states[i] = + !socket_states[i];
						update_attribute(attributes.socket_states.register, socket_states)
					}
				} > Toggle </button>
			</li>
			);
		});

		return rendered_sockets;
	}

	return (
	<div>
		<p>Device enabled: { attributes.enabled.value } &nbsp;
			<button className="set" onClick={ () => update_attribute(attributes.enabled.register, + !attributes.enabled.value) } > Toggle </button>
		</p>
		<ul>
			{ render_socket_states() }
		</ul>
	</div>
	)
}

function Poweroutlet_Schedules({ attributes, schedules, submit_schedule }) {
	const [target_settings, set_target_settings] = useState(Array(attributes.socket_count.value).fill(null));

	const [schedule_params, set_schedule_params] = useState({ });

	function on_update_settings(index, value) {
		let new_settings = [ ...target_settings ];
		new_settings[index] = value;
		set_target_settings(new_settings)
	}

	function on_update_schedule(field, value) {
		let new_params = { ...schedule_params };
		new_params[field] = value;
		set_schedule_params(new_params)
	}

	function add_schedule() {
		let new_schedule = build_schedule(
		  attributes.socket_states.register,
		  target_settings, 
		  schedule_params
		);
		submit_schedule(new_schedule);
	}

	function remove_schedule(id) {
		submit_schedule(build_schedule(null, null, null, "delete", id))
	}

	function render_schedule(obj) {
		return (
			<li key={ JSON.stringify(obj.id) }>
				{ JSON.stringify(obj) }
				<button className="set" onClick={ () => remove_schedule(obj.id) } > Remove </button>
			</li>
		)
	}

	let rendered_schedules = schedules.map((obj) => {
		return render_schedule(obj)
	})

	if (!rendered_schedules.length) {
		rendered_schedules = <p>None</p>;
	}

	let socket_options = target_settings.map((obj, i) => {
		return socket_option(i,on_update_settings);
	})

	return (
	<div>
		<b>Schedules</b>
		<ul>
			{ rendered_schedules }
		</ul>
		<br />
		<b>New Schedule</b>
		<div><span>Socket values&nbsp;
			{ socket_options }
			<br />
			<Schedule_Time_Selector on_update_schedule={ on_update_schedule }/>
			<button className="set" onClick={ () => add_schedule() } > Add </button>
		</span></div>	
	</div>	
	);
}