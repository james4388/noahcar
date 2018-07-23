import React, { PureComponent } from 'react';
require('./Notification.scss')

export default class Notification extends PureComponent {
    constructor(props) {
        super(props);

        this.handleDismiss = this.props.onDismiss || null;
    }

    render() {
        const { notifications } = this.props;
        if (notifications.size > 0) {
            return <div className="notification">
                <ul className="noti-list">
                    { notifications.map((item, key) =>
                        <li className={"alert alert-" + item.get('level')}
                                key={key}>
                            {item.get('content')}
                            {this.handleDismiss ?
                                <button type="button" className="close"
                                    title="Dismiss" onClick={this.handleDismiss}>
                                        <span aria-hidden="true">&times;</span>
                                </button>
                            : null }
                        </li>
                    ) }
                </ul>
            </div>
        }
        return null;
    }
}
