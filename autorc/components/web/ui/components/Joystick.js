/* Nipple js wrapper */
import React, { PureComponent } from 'react';
import PropTypes from 'prop-types';
import { List, Map } from 'immutable';
import { create as createNipple } from 'nipplejs';

require('./Joystick.scss');

export default class Joystick extends PureComponent {
    constructor(props) {
        super(props);
        this.nipple = null;

        this.destroyNipple = this.destroyNipple.bind(this);
        this.setupNipple = this.setupNipple.bind(this);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(evt, data) {
        if(typeof(this.props.onChange) === 'function') {
            this.props.onChange(data);
        }
        return true;
    }

    componentDidUpdate(prevProps) {
        // Check for option change and reinit nipple
        if (prevProps.options !== this.props.options) {
            this.setupNipple(this.props.options);
        }
    }

    setupNipple(options) {
        this.destroyNipple();
        options = options || new Map();
        if (options && !Map.isMap(options)) {
            console.warn('Joystick options must be immutable');
            options = new Map(options);
        }
        if (this.nippleZone) {
            options = options.merge({
                'zone': this.nippleZone,
                'color': options.get('color', 'red'),
                'mode': options.get('mode', 'dynamic'),
                'multitouch': false,
                'size': options.get('size', 150),
                'maxNumberOfNipples': 1,
                'threshold': 0,
                'position': options.get('position', {
                    top: '50%', left: '50%'}),
            });
            this.nipple = createNipple(options.toJS());
            // Handle event;
            if (typeof(this.props.onStart) === 'function'){
                this.nipple.on('start', this.props.onStart)
            }
            if (typeof(this.props.onEnd) === 'function'){
                this.nipple.on('end', this.props.onEnd)
            }
            this.nipple.on('move', this.handleChange);
        }
    }

    destroyNipple() {
        if (this.nipple) {
            this.nipple.destroy && this.nipple.destroy();
            this.nipple = null;
        }
    }

    componentDidMount() {
        // Initialize nipple
        this.setupNipple(this.props.options);
    }

    componentWillUnmount() {
        this.destroyNipple();
    }

    render() {
        const { placeHolder, children } = this.props;
        return <div className="joystick" ref={el => this.nippleZone = el}>
            {placeHolder ?
                <span className="placeHolder">{placeHolder}</span>
            : children}
        </div>
    }
}

Joystick.propTypes = {
    options: PropTypes.instanceOf(Map).isRequired,   //Immutable type
    placeHolder: PropTypes.string,
    onStart: PropTypes.func,
    onChange: PropTypes.func,
    onEnd: PropTypes.func
};
