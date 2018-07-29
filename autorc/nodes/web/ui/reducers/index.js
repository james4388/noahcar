import { combineReducers } from 'redux-immutable'
import { notifications } from 'reducers/notification';
import { websocket } from 'reducers/websocket';
import { chat } from 'reducers/chat';
import { vehicle } from 'reducers/vehicle';

export default combineReducers({
    notifications,
    ws: websocket,
    chat,
    vehicle
});
