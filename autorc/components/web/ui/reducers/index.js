import { combineReducers } from 'redux-immutable'
import { notifications } from './notification';
import { websocket } from './websocket';
import { chat } from './chat';

export default combineReducers({
    notifications,
    ws: websocket,
    chat
});
