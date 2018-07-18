import { combineReducers } from 'redux-immutable'
import { notifications } from './notification';
import { websocket } from './websocket';


export default combineReducers({
    notifications,
    ws: websocket
});
