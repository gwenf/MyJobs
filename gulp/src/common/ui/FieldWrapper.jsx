import React from 'react';
import {map} from 'lodash-compat/collection';

/**
 * Wraps a child field with standardized layout of helptext, error text, and label
 */
class FieldWrapper extends React.Component {
  render() {
    const {label, helpText, errors, children, required, isHidden} = this.props;

    const requiredIndicator = required ? ' *' : '';

    let helpOrErrorText;
    if (errors.length) {
      helpOrErrorText = map(errors, (errorText, i) =>
          <span key={i} className="error-text">{errorText}</span>);
    } else if (helpText) {
      helpOrErrorText = <span className="help-block">{helpText}</span>;
    } else {
      helpOrErrorText = '';
    }

    const rowClasses = isHidden ? 'row hidden' : 'row';

    return (
      <div className={rowClasses}>
        <div className="col-xs-12 col-md-4">
          <label>{label}{requiredIndicator}:</label>
        </div>
        <div className="col-xs-12 col-md-8">
          {children}
          {helpOrErrorText}
        </div>
      </div>
    );
  }
}

FieldWrapper.propTypes = {
  /**
   * Human readable label for user
   */
  label: React.PropTypes.string.isRequired,
  /**
   * Human readable description of information to go in this field
   */
  helpText: React.PropTypes.string,
  /**
   * Array of strings, each a possible error produced by Django
   */
  errors: React.PropTypes.arrayOf(React.PropTypes.string),
  /**
   * Form element for this Component to wrap
   */
  children: React.PropTypes.element.isRequired,
  /**
   * Should the label for this form element have an asterisk to indicate required?
   */
  required: React.PropTypes.bool,
  /**
   * Should this component be shown or not?
   */
  isHidden: React.PropTypes.bool,
};

FieldWrapper.defaultProps = {
  helpText: '',
  errors: [],
  required: false,
  isHidden: false,
};

export default FieldWrapper;
