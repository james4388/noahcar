import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { List, Map } from 'immutable';
import { createStore, applyMiddleware } from 'redux';
import thunkMiddleware from 'redux-thunk';
import rootReducer from 'reducers'
import { connect as wsConnect, emit } from 'actions/websocket';
import MainApp from 'containers/MainApp';
import * as constants from 'constants';
const { WS_STATUS } = constants;

const initialState = new Map({
    'notifications': new List(),
    'ws': new Map({
        'status': WS_STATUS.DISCONNECT,
        'reconnectAttemps': 0,
        'serverShutdown': false
    })
});

const middleware = [thunkMiddleware.withExtraArgument({emit})];
const store = createStore(
    rootReducer, initialState, applyMiddleware(...middleware));

// Init WebSocket
const protocol = window.location.protocol == 'https:' ? 'wss://' : 'ws://';
const wsUri = `${protocol}${window.location.host}/ws`;
store.dispatch(wsConnect(wsUri));

ReactDOM.render(
    <Provider store={store}>
        <MainApp />
    </Provider>,
    document.getElementById('main-container')
);
