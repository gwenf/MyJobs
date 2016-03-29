import React from 'react';

function CheckBox(props) {
  const {name, onChange, required, initial, isHidden} = props;
  return (
    <input
      type="checkbox"
      id={name}
      name={name}
      className=""
      required={required}
      hidden={isHidden}
      defaultChecked={initial}
      onChange={onChange}
      />
  );
}

CheckBox.propTypes = {
  /**
  * Callback: the user edited this field
  *
  * obj: change event
  */
  onChange: React.PropTypes.func.isRequired,
  /**
   * under_score_seperated, unique name of this field. Used to post form
   * content to Django
   */
  name: React.PropTypes.string.isRequired,
  /**
   * Value at first page load
   */
  initial: React.PropTypes.bool,
  /**
   * Should this component be shown or not?
   */
  isHidden: React.PropTypes.bool,
  /**
   * Must this field have a value before submitting form?
   */
  required: React.PropTypes.bool,
};

CheckBox.defaultProps = {
  initial: false,
  isHidden: false,
  required: false,
};

export default CheckBox;
