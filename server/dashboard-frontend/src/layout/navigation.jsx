import { useState } from "react";
import { NavLink, useLocation } from "react-router";
import { isMobile, useMobileOrientation } from "react-device-detect";
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import { theme } from "../styles/theme";
import { logout } from "../utils";

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
		background: theme.light.navbar_color,
		borderRight: theme.border_thin
	},
	nav_item_container: {
		display: "flex",
		alignItems: "center",
		height: "48px",
		borderBottom: theme.border_thin,
		borderRight: theme.border_thin,
		paddingLeft: "16px",
		minWidth: "fit-content",
		width: "168px",
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
		borderRight: theme.border_thin,
		borderBottom: theme.border_thin,
		borderRadius: "0 0 8px",
		background: theme.light.navbar_color
	},
	side_bar_home_link: {
		paddingLeft: "16px",
		borderBottom: theme.border_thin,
		borderRight: theme.border_thin
	}
};

const path_name_map = {
	"/": "Overview",
	"/thermostat": "Thermostats",
	"/poweroutlet": "Power Outlets",
	"/debug": "Debug",
}

export const HomeLink = function({ style }) {
	return (
		<NavLink to="/" style={style}>
			<div style={{ alignItems: "center", display: "flex", flexDirection: "row", gap: "8px" }}>
				<img src="favicon.ico" style={{ height: "32px" }} />	
				<h2>{"EasyDen"}</h2>
			</div>
		</NavLink>
	)
}

export const NavbarSide = function({ managed, close_sidebar }) {
	const nav_items = ["/", "/thermostat", "/poweroutlet"];

	const location = useLocation();
	const { isLandscape } = useMobileOrientation();

	const NavbarContent = function() {
		return (
			<nav className="navbar-side" style={{backgroundColor: theme.light.navbar_color}}>
				{isMobile && isLandscape && <HomeLink style={styles.side_bar_home_link}/>}
				{nav_items.map((item) => (
					<NavLink key={item} to={item} onClick={close_sidebar}>
						<div style={{
							...styles.nav_item_container, 
							...((item == location.pathname || managed) && { borderRight: `1px solid ${theme.light.gutter_color}` }),
							...(item == location.pathname && { backgroundColor: theme.light.gutter_color }),
							}}>
							{path_name_map[item]}
						</div>
					</NavLink>
				))}
				<div style={{
					...styles.nav_item_container,
					...(!managed && { height: "100%" }),
					...(managed && { borderRight: `1px solid ${theme.light.gutter_color}`})
				}}/>
				{/* TODO: Find less lazy solution for this*/}
				<NavLink onClick={logout} >
					<div style={{
						...styles.nav_item_container, 
						...(managed && { borderRight: `1px solid ${theme.light.gutter_color}` })
						}}>
						{"Logout"}
					</div>
				</NavLink>
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

export const NavbarTop = function({ manage_sidebar }) {
	const [ nav_menu_open, set_nav_menu_open ] = useState(!manage_sidebar)
	const location = useLocation();

	return (
		<div className="navbar-top" style={{ display: "flex", flexDirection: "row", gap: "12px", backgroundColor: theme.light.navbar_color }}>
			{
				manage_sidebar && 
				<button style={{ height: "32px" }} onClick={() => set_nav_menu_open(!nav_menu_open) }>
					<MenuIcon />
				</button>
			}
			<HomeLink/>
			<div style={{ alignItems: "inherit", display: "flex", flexDirection: "row", gap: "8px" }}>
				<p>&#x2022;</p>
				<h3>{path_name_map[location.pathname] || location.pathname.substring(1)}</h3>
			</div>
			{ manage_sidebar && nav_menu_open && <NavbarSide managed={manage_sidebar} close_sidebar={() => set_nav_menu_open(false)} /> }
		</div>
	)
}
