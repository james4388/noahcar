import * as constants from 'constants';

let notiTimeout = null;

export function clearNotification() {
    return {
        type: constants.CLEAR_GLOBAL_NOTIFICATION
    }
}

export function showNotification(message, level='danger', autoHide=null) {
    return (dispatch, getState) => {
        dispatch({
            type: constants.ADD_GLOBAL_NOTIFICATION,
            message: {
                level: level,
                content: message
            }
        });
        if (autoHide) {
            clearTimeout(notiTimeout);
            notiTimeout = setTimeout(function() {
                dispatch(clearNotification())
            }, autoHide);
        }
    }
}
