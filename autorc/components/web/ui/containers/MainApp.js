import React, { Component } from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import { clearNotification, showNotification } from 'actions/notification';
import { sendMessage } from 'actions/chat';
import Notification from 'components/Notification';

class MainApp extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        const { notifications, chat, actions } = this.props;
        return <div className="main-app container-fluid">
            <Notification
                notifications={notifications}
                onDismiss={actions.notifications.clearNotification}
            />
            <div className="row">
                <div className="col-sm-4">Camera</div>
                <div className="col-sm-8">Stats</div>
            </div>
            <div className="controller row">
                <div className="col">Throttle</div>
                <div className="col">Stearing</div>
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
            'chat': bindActionCreators({sendMessage}, dispatch)
        }
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(MainApp);
