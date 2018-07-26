import React, { Component } from 'react';
import { List, Map } from 'immutable';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { clearNotification, showNotification } from 'actions/notification';
import { steering, throttle } from 'actions/vehicle';
import { sendMessage } from 'actions/chat';
import Notification from 'components/Notification';
import JoystickController from 'components/JoystickController';

require('./MainApp.scss');

class MainApp extends Component {
    constructor(props) {
        super(props);
        this.state = {
            steering: 0,
            throttle: 0
        }

        this.steer = this.steer.bind(this);
        this.throttle = this.throttle.bind(this);
    }

    steer(val) {
        this.setState({steering: 360 * val});
        this.props.actions.vehicle.steering(val);
    }

    throttle(val) {
        this.setState({throttle: val});
        this.props.actions.vehicle.throttle(val);
    }

    render() {
        const { notifications, chat, actions } = this.props;
        const { steering, throttle } = this.state;
        return <div className="main-app">
            <Notification
                notifications={notifications}
                onDismiss={actions.notifications.clearNotification}
            />
            <div className="camera-view">
                <img src="/mjpeg_stream" alt="Fetching camera view"/>
            </div>
            <div className="steering-visualize">
                <img src="/static/images/steeringwheel.png" style={{transform: `rotate(${steering}deg)`}} alt="☺"/>
            </div>
            <div className="stats">
                Stats. Speed: {throttle}. Steer: {steering}.<br/>
            </div>
            <JoystickController onThrottleChange={this.throttle} onSteeringChange={this.steer}/>
        </div>
    }
}

function mapStateToProps(state) {
    return {
        notifications: state.get('notifications'),
        chat: state.get('chat')
    }
}

function mapDispatchToProps(dispatch) {
    return {
        dispatch: dispatch,
        actions: {
            'notifications': bindActionCreators({
                clearNotification, showNotification
            }, dispatch),
            'chat': bindActionCreators({sendMessage}, dispatch),
            'vehicle': bindActionCreators({steering, throttle}, dispatch)
        }
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(MainApp);
