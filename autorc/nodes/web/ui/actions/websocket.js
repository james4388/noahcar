/* Handle websocket connection, auto reconnect on connection error
   Convert all socket data to actions
*/
import * as constants from 'constants';
import { rangeMap } from 'utils';
import { showNotification } from 'actions/notification';

let ws = null;

function destroySocket() {
    if (ws !== null) {
        ws.onopen = ws.onmessage = ws.onclose = ws.onerror = null;
    }
    ws = null;
}

function tryToReconnect(wsUri, dispatch, getState) {
    const wsState = getState().get('ws') || new Map();
    const reconnectAttemps = wsState.get('reconnectAttemps');
    const isServerShutdown = wsState.get('serverShutdown');
    if (!isServerShutdown && reconnectAttemps <=
            constants.WS_MAX_RECONNECT_ATTEMPS) {
        dispatch(connect(wsUri, true));
        return true;
    }
    return false;
}

export function disconnect() {
    return (dispatch, getState) => {
        if (ws !== null) {
            try {
                ws.close();
            } catch (ex) {
                console.log(`Error when disconnect ${ex}`);
            }
        }
        destroySocket();
        dispatch({type: constants.DISCONNECT_RESPONSE})
    }
}


export function connect(wsUri, reconnect=false) {
    // Connect websocket to server
    return (dispatch, getState) => {
        if (reconnect) {
            destroySocket();
            dispatch({type: constants.RECONNECT_REQUEST});
        } else {
            dispatch(disconnect());
            dispatch({type: constants.CONNECT_REQUEST});
        }
        ws = new WebSocket(wsUri);
        ws.onopen = function() {
            dispatch({type: constants.CONNECT_RESPONSE});
        };
        ws.onmessage = function(event) {
            let data = null;
            try {
                data = JSON.parse(event.data);
            } catch (ex) {
                console.log('Invalid or broken data', ex);
                dispatch(showNotification('Invalid or broken data', 'danger'));
                return;
            }
            const { action, ...payload } = data;
            console.log('Got mess froms srv', action, payload);
            dispatch({type: action, payload});
        };
        // TODO handle websocket error https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent
        ws.onclose = function(event) {
            console.log('server close', event.code);
            switch (event.code) {   // Close code
                case 1000:	// CLOSE_NORMAL
                    dispatch(showNotification('Server is shutting down'));
        			dispatch({type: constants.SERVER_SHUTDOWN});
        			break;
                default:	// Abnormal closure
                    if (tryToReconnect(wsUri, dispatch, getState)) {
                        return;
                    }
    			    break;
            }
            dispatch(disconnect());
        };
        ws.onerror = function(event) {
            switch (event.code) {
                case 'ECONNREFUSED':
                    if (tryToReconnect(wsUri, dispatch, getState)) {
                        return;
                    }
        			break;
            }
        }
    }
}


export function emit(action, data) {
    // Send data to server via websocket
    if (ws !== null) {
        ws.send(JSON.stringify({
            ...data,
            'action': action,
        }));
    }
}
