import Immutable, {List, Map} from 'immutable';
import * as constants from 'constants';

export function notifications(state = new List(), action) {
    switch (action.type) {
        case constants.ADD_GLOBAL_NOTIFICATION:
            return state.push(Immutable.fromJS(action.message));
        case constants.CLEAR_GLOBAL_NOTIFICATION:
            return new List();
        default:
            return state;
    }
}
