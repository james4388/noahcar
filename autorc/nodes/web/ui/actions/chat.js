import * as constants from 'constants';

export function sendMessage(message) {
    return (dispatch, getState, {emit}) => {
        console.log(constants.SEND_MESSAGE_REQUEST, {message});
        console.log(emit);
        emit(constants.SEND_MESSAGE_REQUEST, {message});
    }
}
