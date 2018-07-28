import React, { Component } from 'react';
import screenfull from 'screenfull';
import { List, Map } from 'immutable';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { clearNotification, showNotification } from 'actions/notification';
import {
    steering, throttle, startTrainingRecord, endTrainingRecord
} from 'actions/vehicle';
import { sendMessage } from 'actions/chat';
import Notification from 'components/Notification';
import JoystickController from 'components/JoystickController';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
    faExpand, faCompress, faVideo, faVideoSlash
} from '@fortawesome/free-solid-svg-icons';

require('./MainApp.scss');

class MainApp extends Component {
    constructor(props) {
        super(props);
        this.state = {
            steering: 0,
            throttle: 0,
            fullscreen: false,
            fullscreenEnable: screenfull.enabled,
            recordEnable: false
        }

        this.steer = this.steer.bind(this);
        this.throttle = this.throttle.bind(this);
        this.toggleFullScreen = this.toggleFullScreen.bind(this);
        this.onFullScreenChange = this.onFullScreenChange.bind(this);
        this.onRecordChange = this.onRecordChange.bind(this);
    }

    componentDidMount() {
        if (screenfull.enabled) {
            screenfull.on('change', this.onFullScreenChange);
        }
    }

    componentWillUnmount() {
        screenfull.off('change', this.onFullScreenChange);
    }

    onRecordChange() {
        this.setState({
            recordEnable: !this.state.recordEnable
        }, () => {
            if (this.state.recordEnable) {
                this.props.actions.vehicle.startTrainingRecord();
            } else {
                this.props.actions.vehicle.endTrainingRecord();
            }
        });
    }

    toggleFullScreen() {
        if(this.el) {
            screenfull.toggle(this.el);
        }
    }

    onFullScreenChange() {
        this.setState({fullscreen: screenfull.isFullscreen});
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
        const {
            steering, throttle, fullscreenEnable, fullscreen, recordEnable
        } = this.state;
        return <div className="main-app" ref={el => this.el = el}>
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
            <div className="action-buttons">
                {fullscreenEnable ? <button onClick={this.toggleFullScreen} title="Fullscreen">
                    <FontAwesomeIcon size="3x" icon={fullscreen ? faCompress : faExpand} />
                </button> : null}
                <button onClick={this.onRecordChange} title="Record on run">
                    <FontAwesomeIcon size="3x" icon={recordEnable ? faVideoSlash : faVideo } />
                </button>
            </div>
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
            'vehicle': bindActionCreators({
                steering, throttle, startTrainingRecord, endTrainingRecord
            }, dispatch)
        }
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(MainApp);
