import React from 'react';

class BasicCheckBox extends React.Component {
  render() {
    let requiredIndicator = '';
    if (this.props.required) {
      requiredIndicator = ' *';
    }

    let helpOrErrorText;
    // Check if this field appears in the list of error messages passed down
    if (this.props.errorMessages.hasOwnProperty(this.props.name)) {
      helpOrErrorText = <span className="error-text">{this.props.errorMessages[this.props.name]}</span>;
    } else if ((this.props.help_text)) {
      helpOrErrorText = <span className="help-block">{this.props.help_text}</span>;
    }

    return (
      <div className="row">
        <div className="col-xs-12 col-md-4">
          <lable>{this.props.label}{requiredIndicator}:</lable>
        </div>
        <div className="col-xs-12 col-md-8">
          <input
            type="checkbox"
            defaultChecked={this.props.initial}
            id={this.props.name}
            name={this.props.name}
            required={this.props.required}
            hidden={this.props.widget.is_hidden}
            onChange={this.props.onChange}
            />
          {helpOrErrorText}
        </div>
      </div>
    );
  }
}

BasicCheckBox.propTypes = {
  onChange: React.PropTypes.func.isRequired,
  label: React.PropTypes.string.isRequired,
  name: React.PropTypes.string.isRequired,
  placeholder: React.PropTypes.string,
  initial: React.PropTypes.bool,
  widget: React.PropTypes.object,
  required: React.PropTypes.bool,
  help_text: React.PropTypes.string,
  errorMessages: React.PropTypes.object,
};

BasicCheckBox.defaultProps = {
  initial: '',
  placeholder: '',
  widget: {},
  label: '',
  required: false,
  name: '',
  help_text: '',
  errorMessages: {},
};

export default BasicCheckBox;
