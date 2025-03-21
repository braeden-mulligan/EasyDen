import { useState } from "react";
import { NavLink, useLocation } from "react-router";
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';

const styles = {
	managed_side_bar_container: {
		position: "fixed",
		top: "0",
		left: "0",
		height: "100%",
		display: "flex",
		flexDirection: "row"
	},
	managed_side_bar: {
		height: "100%",
		background: "white",
		borderRight: "1px solid grey"
	},
	nav_item_container: {
		display: "flex",
		alignItems: "center",
		height: "48px",
		borderBottom: "1px solid grey",
		borderRight: "1px solid grey",
		paddingLeft: "16px",
		minWidth: "fit-content",
		width: "150px",
	},
	nav_item_text: {
		textDecoration: "none",
		color: "black"
	},
	nav_item_css: `
		.navbar-side a:hover {
			background: lightgrey;
			cursor: auto
		}
	`,
	side_bar_back_button: {
		height: "49px",
		width: "48px",
		borderLeft: "none",
		borderTop: "none",
		borderRight: "1px solid grey",
		borderBottom: "1px solid grey",
		borderRadius: "0 0 8px",
		background: "white"
	}
};

const path_name_map = {
	"/": "Overview",
	"/thermostat": "Thermostats",
	"/poweroutlet": "Power Outlets",
	"/debug": "Debug",
}

export const NavbarSide = function ({ managed, close_sidebar }) {
	console.log("managed?", managed);
	const nav_items = ["/", "/thermostat", "/poweroutlet"];

	const location = useLocation();

	const NavbarContent = function() {
		return (
			<nav className="navbar-side">
				{nav_items.map((item) => (
					<NavLink key={item} to={item} style={styles.nav_item_text} onClick={close_sidebar}>
						<div style={{
							...styles.nav_item_container, 
							...((item == location.pathname || managed) && { borderRight: "none" }),
							}}>
							{path_name_map[item]}
						</div>
					</NavLink>
				))}
				{!managed && <div style={{
					...styles.nav_item_container, 
					height: "100%"}}/>
				}
				<style>{styles.nav_item_css}</style>
			</nav>
		)
	}

	return managed ? (
		<div style={styles.managed_side_bar_container}>
			<div style={styles.managed_side_bar}>
				<NavbarContent/>
			</div>
			<button style={styles.side_bar_back_button} onClick={close_sidebar}>
				<ChevronLeftIcon />
			</button>
		</div>
	) : (
		<NavbarContent/>
	)
}

export const NavbarTop = function ({ manage_sidebar }) {
	const [ nav_menu_open, set_nav_menu_open ] = useState(!manage_sidebar)
	const location = useLocation();

	return (
		<div className="navbar-top" style={{ display: "flex", flexDirection: "row", gap: "12px" }}>
			{
				manage_sidebar && 
				<button style={{ height: "32px" }} onClick={() => set_nav_menu_open(!nav_menu_open) }>
					<MenuIcon />
				</button>
			}
			<NavLink to="/" >
				<img src="favicon.ico" style={{ height: "32px" }} />	
			</NavLink>
			{ manage_sidebar && nav_menu_open && <NavbarSide managed={manage_sidebar} close_sidebar={() => set_nav_menu_open(false)} /> }
			<div style={{ alignItems: "inherit", display: "flex", flexDirection: "row", gap: "8px" }}>
				<h2>{"EasyDen"}</h2>
				<p>&#x2022;</p>
				<h3>{path_name_map[location.pathname] || location.pathname.substring(1)}</h3>
			</div>
		</div>
	)
}
