import { create } from 'zustand'
import { equal } from './utils'

export const useGlobalStore = create((set) => ({
	devices: [],
	notifications: [],
	clear_notifications: () => set((state) => ({
		notifications: []
	}))
}));

export const add_notification = function(notification) {
	useGlobalStore.setState((state) => state.notifications = [...state.notifications, JSON.stringify(notification)]);
};

export const update_device_list = function(devices) {
	const current_devices = [...useGlobalStore.getState().devices];

	for (const device of devices) {
		let device_index = current_devices.findIndex((d) => device.id === d.id);
		
		if (device_index > -1) {
			current_devices[device_index] = device;
		} else {
			current_devices.push(device);
		}
	};

	if (equal(useGlobalStore.getState().devices, current_devices)) return;

	useGlobalStore.setState((state) => state.devices = current_devices);
};