import React, { Component } from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import { clearNotification, showNotification } from '../actions/notification';
import { chat } from '../actions/chat';
import Notification from '../components/Notification';

class MainApp extends Component {
    constructor(props) {
        super(props);

        this.addMessage = this.addMessage.bind(this);
        this.sendMessage = this.sendMessage.bind(this);
        this.msgChange = this.msgChange.bind(this);

        this.state = {
            msg: ''
        }
    }

    msgChange(evt) {
        this.setState({msg: evt.target.value});
    }

    sendMessage() {
        const {msg} = this.state;
        this.props.actions.chat.chat(msg);
        this.setState({msg: ''});
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
        const { notifications, chat } = this.props;
        const { msg } = this.state;
        return <div className="main-app container-fluid">
            <Notification
                notifications={notifications}
                onDismiss={this.props.actions.notifications.clearNotification}
            />
            <button onClick={this.addMessage}>Add message</button>
            <div style={{border: '1px solid black', width: '400px', 'maxHeight': '300px'}}>
                {chat.map(msg => <p key={msg}>{msg}</p>)}
            </div>
            <input value={msg} onChange={this.msgChange}/><button onClick={this.sendMessage}>Send</button>
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
            'chat': bindActionCreators({chat}, dispatch)
        }
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(MainApp);
