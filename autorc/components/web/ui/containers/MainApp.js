import React, { Component } from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import { clearNotification, showNotification } from '../actions/notification';
import Notification from '../components/Notification';

class MainApp extends Component {
    constructor(props) {
        super(props);

        this.addMessage = this.addMessage.bind(this);
    }

    addMessage() {
        let msg = prompt('Enter mess');
        if (msg === 'clear') {
            this.props.actions.notifications.clearNotification();
        } else {
            this.props.actions.notifications.showNotification(msg);
        }
    }

    render() {
        const { notifications } = this.props;
        return <div className="main-app container-fluid">
            <Notification
                notifications={notifications}
                onDismiss={this.props.actions.notifications.clearNotification}
            />
            <button onClick={this.addMessage}>Add message</button>
        </div>
    }
}

function mapStateToProps(state) {
    return {
        notifications: state.get('notifications')
    }
}

function mapDispatchToProps(dispatch) {
    return {
        dispatch: dispatch,
        actions: {
            'notifications': bindActionCreators({
                clearNotification, showNotification
            }, dispatch)
        }
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(MainApp);
