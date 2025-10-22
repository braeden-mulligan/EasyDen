import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from "react-router"
import { isMobile, useMobileOrientation } from "react-device-detect";
import { useGlobalStore } from './store';

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
import { theme } from './styles/theme';

function AppMain() {
	const { isPortrait, isLandscape } = useMobileOrientation();
	const mobile_portrait = isMobile && isPortrait;
	const mobile_landscape = isMobile && isLandscape;

	const user = useGlobalStore((state) => state.user);

	return (
		<BrowserRouter>
			{!mobile_landscape && <NavbarTop manage_sidebar={mobile_portrait} />}
			<div className="layout-main">
				{!mobile_portrait && <NavbarSide />}
				<div className="content-main" style={{backgroundColor: theme.light.gutter_color}}>
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