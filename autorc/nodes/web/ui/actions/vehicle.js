/* Vehicle controller action */
import * as constants from 'constants';

export function steering(value) {
    return (dispatch, getState, {emit}) => {
        console.log('Steer', value);
        emit(constants.VEHICLE_STEER, {value});
    }
}

export function throttle(value) {
    return (dispatch, getState, {emit}) => {
        console.log('Thrott', value);
        emit(constants.VEHICLE_THROTTLE, {value});
    }
}
