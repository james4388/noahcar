import Immutable, { Map } from 'immutable';
import * as constants from 'constants';
const { WS_STATUS } = constants;

export function websocket(state=new Map(), action) {
    switch (action.type) {
        case constants.DISCONNECT_RESPONSE:
            return state.set('status', WS_STATUS.DISCONNECT);
        case constants.CONNECT_REQUEST:
            return state.set('status', WS_STATUS.CONNECTING)
                        .update('reconnectAttemps', 0, v => v + 1);
        case constants.CONNECT_RESPONSE:
            return state.set('status', WS_STATUS.CONNECTED)
                .set('reconnectAttemps', 0);
        case constants.SERVER_SHUTDOWN:
            return state.set('serverShutdown', true);
        default:
            return state;
    }
}
