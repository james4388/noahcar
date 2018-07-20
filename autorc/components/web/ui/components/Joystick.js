/* Nipple js wrapper */
import React, { PureComponent } from 'react';
import PropTypes from 'prop-types';
import { create as createNipple } from 'nipplejs';
import { rangeMap } from 'utils';

export default class Joystick extends PureComponent {
    constructor(props) {
        super(props);
        this.nipple = null;
    }

    componentDidMount() {
        // Initialize nipple
        this.nipple = createNipple({

        });
    }

    componentWillUnmount() {
        // Destroy nipple instance
    }

    render() {
        return <div className="joystick">

        </div>
    }
}

Joystick.propTypes = {
    name: PropTypes.string
};
