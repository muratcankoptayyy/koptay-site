import {configureStore} from '@reduxjs/toolkit';
import userReducer from './slices/userSlice';
import queueSlice from './slices/queueSlice';
import notificationReducer from './slices/notificationSlice';

export const store = configureStore({
	reducer: {
		user: userReducer,
		queue: queueSlice,
		notifications: notificationReducer
	},
});

