import Immutable, {List, Map} from 'immutable';
import * as constants from 'constants';

export function chat(state = new List(), action) {
    console.log(action);
    switch (action.type) {
        case constants.SEND_MESSAGE_RESPONSE:
            return state.push(Immutable.fromJS(
                `${action.payload.user.name}: ${action.payload.message}`));
        default:
            return state;
    }
}
