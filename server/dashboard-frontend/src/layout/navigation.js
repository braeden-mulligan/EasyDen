import { useState } from "react";
import { NavLink, useLocation } from "react-router";
import MenuIcon from '@mui/icons-material/Menu';

export const NavbarSide = function () {
	return (
		<nav>
			<NavLink to="/">Overview</NavLink>
			<NavLink to="/thermostat">Thermostats</NavLink>
			<NavLink to="/poweroutlet">Power Outlets</NavLink>
		</nav>
	)
}

export const NavbarTop = function ({ manage_sidebar }) {
	const [ nav_menu_open, set_nav_menu_open ] = useState(!manage_sidebar)
	const location = useLocation();

	const path_map = {
		"/": "Overview",
		"/thermostat": "Thermostats",
		"/poweroutlet": "Power Outlets",
		"/debug": "Debug",
	}

	return (
		<div style={{ display: "flex", flexDirection: "row" }}>
			{
				manage_sidebar && 
				<button style={{ height: "32px" }} onClick={() => set_nav_menu_open(!nav_menu_open) }>
					<MenuIcon />
				</button>
			}
			<NavLink to="/" >
				<img src="favicon.ico" style={{ height: "32px" }} />	
			</NavLink>
			{ manage_sidebar && nav_menu_open && <NavbarSide /> }
			<h2>{`EasyDen - ${path_map[location.pathname] || location.pathname.substring(1)}` }</h2>
		</div>
	)
}
