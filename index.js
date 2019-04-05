const h = require('react-hyperscript');
const React = require('react');
const ReactDOM = require('react-dom');
const hh = require('hyperscript-helpers')(h);


class Input extends React.Component {
    constructor(props, ...args) {
        super(props, ...args);
        this.state = { value: props.value };
    }

    componentWillReceiveProps(nextProps) {
        if (this.state.value !== nextProps.value) {
            this.setState({ value: nextProps.value });
        }
    }

    onChange(event) {
        event.persist();
        this.setState({ value: event.target.value }, () => this.props.onChange(event));
    }

    render() {
	let properties = Object.assign({}, this.props);
	properties = Object.assign(properties, this.state);
	properties['onChange'] = this.onChange.bind(this);
	return h('input', properties, []);
    }
}


export default {h, ReactDOM, Input};
