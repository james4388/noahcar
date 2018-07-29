import Immutable, {List, Map} from 'immutable';
import * as constants from 'constants';

export function vehicle(state = new Map(), action) {
    switch (action.type) {
        case constants.VEHICLE_STATS_RESPONSE:
            // Only vehicle stat for now;
            if (action.payload && action.payload.vehicle_stats) {
                return state.merge(action.payload.vehicle_stats);
            }
        default:
            return state;
    }
}
