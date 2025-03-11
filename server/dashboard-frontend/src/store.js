import { create } from 'zustand'

export const useStore = create((set) => ({
	notifications: [],
	clear_notifications: () => set((state) => ({
		notifications: []
	}))
}))

export const add_notification = function(notification) {
	useStore.setState((state) => state.notifications = [...state.notifications, JSON.stringify(notification)])
}