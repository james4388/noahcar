/*  Controller class report throttle and steering update
    JoystickController: controll using virtual Joystick
    Mapping range from -100% -> 100%
*/
import React, { PureComponent } from 'react';
import PropTypes from 'prop-types';
import { List, Map } from 'immutable';
import { rangeMap } from 'utils';
import Joystick from 'components/Joystick';

export default class JoystickController extends PureComponent {
    constructor(props) {
        super(props);
        const { size } = props;

        this.state = {
            throttle: 0,
            steering: 0,
            throttleInControl: false,
            steeringInControl: false
        };
        this.updateHandle = null;
        this.steeringDecelerateHandle = null;

        this.throttleOptions = new Map({
            lockY: true, color: 'red', size: props.size});
        this.steeringOptions = new Map({
            lockX: true, color: 'green', size: props.size});
        this.beginThrottle = this.inControlChange.bind(this, 'throttle', true);
        this.endThrottle = this.inControlChange.bind(this, 'throttle', false);
        this.beginSteering = this.inControlChange.bind(this, 'steering', true);
        this.endSteering = this.inControlChange.bind(this, 'steering', false);
        this.throttleChange = this.throttleChange.bind(this);
        this.steeringChange = this.steeringChange.bind(this);
        this.updateControl = this.updateControl.bind(this);
        this.steeringDecelerate = this.steeringDecelerate.bind(this);
        this.startSteeringDecelerate = this.startSteeringDecelerate.bind(this);
    }

    startSteeringDecelerate() {
        const { steeringDecelerateDelay, steeringDecelerate } = this.props;
        this.updateControl('steering');
        this.steeringDecelerateHandle = setTimeout(
            this.steeringDecelerate, steeringDecelerateDelay);
    }

    steeringDecelerate() {
        const { steering } = this.state;
        const { steeringDecelerateDelay, steeringDecelerate } = this.props;
        if (Math.abs(steering) - steeringDecelerate > 0) {
            this.setState({
                steering: steering > 0 ? steering - steeringDecelerate : steering + steeringDecelerate
            }, this.startSteeringDecelerate);
        } else {
            this.setState({steering: 0});
            this.updateControl('steering');
        }
    }

    inControlChange(ctl, inControl) {
        // Change throttle or steering in control status
        let newState = {
            [`${ctl}InControl`]: inControl
        };

        if (!inControl) {   // Decelerate instead of hard 0
            if (ctl === 'steering') {
                this.startSteeringDecelerate();
            } else {
                newState['throttle'] = 0
            }
        } else {
            if (ctl === 'steering') {
                clearTimeout(this.steeringDecelerateHandle);
            }
        }

        this.setState(newState, () => {
            const { throttleInControl, steeringInControl } = this.state;
            if (!throttleInControl && !steeringInControl) {
                clearInterval(this.updateHandle);
                this.updateHandle = null;
            } else {
                if (!this.updateHandle) {
                    this.updateHandle = setInterval(
                        this.updateControl, this.props.updateDelay);
                }
            }
            this.updateControl(ctl);
        });
    }

    updateControl(force) {
        const {
            throttleInControl, steeringInControl, throttle, steering
        } = this.state;
        const { onThrottleChange, onSteeringChange } = this.props;
        if (throttleInControl || force === 'throttle') {
            if (typeof(onThrottleChange) === 'function') {
                onThrottleChange(throttle);
            }
        }
        if (steeringInControl || force === 'steering') {
            if (typeof(onSteeringChange) === 'function') {
                onSteeringChange(steering);
            }
        }
    }

    convertJoystickValue(joystick, positiveDir) {
        const {steeringZeroThreshold} = this.props;
        if (joystick.force > steeringZeroThreshold && joystick.direction) {
            const { direction } = joystick;
            const sign = (
                direction.y === positiveDir || direction.x === positiveDir
            ) ? 1 : -1;
            return joystick.force > 1 ? sign : sign * joystick.force;
        }
        return 0;
    }

    throttleChange(joystick) {
        const { onThrottleChange } = this.props;
        const throttle = this.convertJoystickValue(joystick, 'up');
        this.setState({throttle});
        if (typeof(onThrottleChange) === 'function') {
            onThrottleChange(throttle);
        }
    }

    steeringChange(joystick) {
        const { onSteeringChange } = this.props;
        const steering = this.convertJoystickValue(joystick, 'right');
        this.setState({steering});
        if (typeof(onSteeringChange) === 'function') {
            onSteeringChange(steering);
        }
    }

    render() {
        return <div className="joystick-controller">
            <div className="left joystick-col">
                <Joystick
                    options={this.throttleOptions}
                    onStart={this.beginThrottle}
                    onChange={this.throttleChange}
                    onEnd={this.endThrottle}
                    placeHolder="Touch for throttle"/>
            </div>
            <div className="right joystick-col">
                <Joystick
                    options={this.steeringOptions}
                    onStart={this.beginSteering}
                    onChange={this.steeringChange}
                    onEnd={this.endSteering}
                    placeHolder="Touch for steering"/>
            </div>
        </div>
    }
}

JoystickController.propTypes = {
    updateDelay: PropTypes.number,
    size: PropTypes.number,             // Joystick size
    onThrottleChange: PropTypes.func,
    onSteeringChange: PropTypes.func,
    steeringZeroThreshold: PropTypes.number,
    steeringDecelerate: PropTypes.number
}

JoystickController.defaultProps = {
    updateDelay: 100,
    size: 150,
    steeringZeroThreshold: 0.05,  // < this mean zero steering
    steeringDecelerate: 0.1,      // Percent
    steeringDecelerateDelay: 50
}
