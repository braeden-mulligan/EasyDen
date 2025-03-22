import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from "react-router"
import { isMobile, useMobileOrientation } from "react-device-detect";

import { NavbarTop, NavbarSide } from "./layout/navigation";
import { NotificationSnackbar } from "./layout/notification";
import { DebugPage } from "./pages/debug";
import { OverviewPage } from "./pages/overview";
import { ThermostatPage } from "./pages/thermostat";
import { PowerOutletPage } from "./pages/poweroutlet";
import { NotFoundPage } from "./pages/not-found";

import "./styles/main-layout.css"
import "./styles/theme.css"
import "./styles/common.css"

function AppMain() {
	const { isPortrait } = useMobileOrientation();
	const narrow_view = isMobile && isPortrait;

	return (
		<BrowserRouter>
			<NavbarTop manage_sidebar={narrow_view} />
			<div className="layout-main">
				{!narrow_view && <NavbarSide />}
				<div className="content-main">
					<Routes>
						<Route path="/" element={<OverviewPage />} />
						<Route path="thermostat" element={<ThermostatPage />} />
						<Route path="poweroutlet" element={<PowerOutletPage/>} />
						<Route path="debug" element={<DebugPage />} />
						<Route path="*" element={<NotFoundPage />} />
					</Routes>
				</div>
			</div>
			<NotificationSnackbar />
		</BrowserRouter>
	);
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<AppMain />);