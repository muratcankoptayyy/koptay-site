import {createSlice} from '@reduxjs/toolkit';

const initialState = {
	myQueue: [],
	joinQueue: [],
};

export const queueSlice = createSlice({
	name: 'queue',
	initialState,
	reducers: {
		setMyQueue: (state, action) => {
			state.myQueue = action.payload;
		},
		setJoinQueue: (state, action) => {
			state.joinQueue = action.payload;
		},
		addToMyQueue: (state, action) => {
			state.myQueue.push(action.payload);
		},
		removeFromMyQueue: (state, action) => {
			state.myQueue = state.myQueue.filter((queue) => queue._id !== action.payload);
		},
		removeFromJoinQueue: (state, action) => {
			state.joinQueue = state.joinQueue.filter((queue) => queue._id !== action.payload);
		},
	},
});

export const {setMyQueue, setJoinQueue, addToMyQueue, removeFromMyQueue, removeFromJoinQueue} = queueSlice.actions;
export default queueSlice.reducer;
