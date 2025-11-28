import {createSlice} from '@reduxjs/toolkit';

const initialState = {
	userToken: typeof window !== 'undefined' && localStorage.getItem('userToken') || null,
	user: typeof window !== 'undefined' && JSON.parse(localStorage.getItem('user')) || null,
};

export const userSlice = createSlice({
		name: 'user',
		initialState,
		reducers: {
			login: (state, action) => {
				state.userToken = action.payload.token;
				state.user = action.payload.user;

				localStorage.setItem('userToken',action.payload.token);
				localStorage.setItem('user', JSON.stringify(action.payload.user));
			},
			logout: (state) => {
				try {

					state.userToken = null;
					state.user = null;

					// localstorage clear

					window.localStorage.removeItem('userToken');

					localStorage.removeItem('userToken');
					localStorage.removeItem('user');

					// clear cookies

					document.cookie = 'userToken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
					document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
					document.cookie = 'user=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';

				}
				catch (e) {
					console.log(e);
				}

			},
			updateUser: (state, action) => {
				state.user = action.payload;
				localStorage.setItem('user', JSON.stringify(action.payload));
			},
			updatePhone: (state, action) => {
				state.user.phone = action.payload;
				localStorage.setItem('user', JSON.stringify(state.user));
			},
			updateEmail: (state, action) => {
				state.user.email = action.payload;
				localStorage.setItem('user', JSON.stringify(state.user));
			},
			updateUserVerify: (state, action) => {
				state.user.user_verify_at = action.payload;
				localStorage.setItem('user', JSON.stringify(state.user));

			},
		},
	},
);

export const {login, logout, updateUserVerify, updateUser, updatePhone, updateEmail} = userSlice.actions;
export default userSlice.reducer;