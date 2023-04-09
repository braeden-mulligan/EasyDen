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
	const [target_settings, set_target_settings] = useState([]);

	const [schedule_params, set_schedule_params] = useState({ });

	function on_update_schedule(field, value) {
		let new_params = { ...schedule_params };
		new_params[field] = value;
		set_schedule_params(new_params)
	}

	function add_schedule() {
		let new_schedule = build_schedule(
		  attributes.target_temperature.register,
		  target_temperature, 
		  schedule_params
		)
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

	let rendered_schedules = schedules.map((obj, i) => {
		return render_schedule(obj, i)
	})

	if (!rendered_schedules.length) {
		rendered_schedules = <p>None</p>;
	}

//TODO: Dehackify this
	return (
	<div>
		<b>Schedules</b>
		<ul>
			{ rendered_schedules }
		</ul>
		<br />
		<b>New Schedule</b>
		<div><span>Socket values&nbsp;
			<input type="text" onChange={ 
				(e) => { 
					let current_target = [];
					for (let i = 0; i < attributes.socket_count.value; ++i) {
						current_target.push(parseInt(e.target.value))
					}
					set_target_settings(current_target)
				}
			} />
			<br />
			<Schedule_Time_Selector on_update_schedule={ on_update_schedule }/>
			<button className="set" onClick={ () => submit_schedule( add_schedule()) } > Add </button>
		</span></div>	
	</div>	
	);
}