import React, {PropTypes, Component} from 'react';
import warning from 'warning';
import {getDisplayForValue} from 'common/array.js';
import TextField from 'common/ui/TextField';
import CheckBox from 'common/ui/CheckBox';
import Textarea from 'common/ui/Textarea';
import DateField from 'common/ui/DateField';
import Select from 'common/ui/Select';
import FieldWrapper from 'common/ui/FieldWrapper';

export default class RemoteFormField extends Component {
  render() {
    const {fieldName, form, value, onChange} = this.props;
    const field = form.fields[fieldName] || {};
    const errors = (form.errors || {})[fieldName];
    const fieldDisable = field.readonly;

    function wrap(child) {
      return (
        <FieldWrapper
          label={field.label}
          helpText={field.help_text}
          errors={errors}
          required={field.required}>
          {child}
        </FieldWrapper>
      );
    }

    const inputType = (field.widget || {}).input_type || 'unspecified';

    switch (inputType) {
    case 'time':
    case 'datetime':
    case 'text':
      return wrap(
        <TextField
          name={fieldName}
          onChange={e => onChange(e, fieldName)}
          required={field.required}
          value={value}
          maxLength={field.widget.maxlength}
          isHidden={field.widget.is_hidden}
          placeholder={field.widget.attrs.placeholder}
          autoFocus={field.widget.attrs.autofocus}
          disable={fieldDisable}
          />
      );
    case 'textarea':
      return wrap(
        <Textarea
          name={fieldName}
          onChange={e => onChange(e, fieldName)}
          required={field.required}
          initial={field.initial}
          maxLength={field.widget.maxlength}
          isHidden={field.widget.is_hidden}
          placeholder={field.widget.attrs.placeholder}
          autoFocus={field.widget.attrs.autofocus}
          disable={fieldDisable}
          />
      );
    case 'date':
      return wrap(
        <DateField
          name={fieldName}
          onChange={e => onChange(e, fieldName)}
          required={field.required}
          value={value}
          maxLength={field.widget.maxlength}
          isHidden={field.widget.is_hidden}
          placeholder={field.widget.attrs.placeholder}
          autoFocus={field.widget.attrs.autofocus}
          numberOfYears={50}
          disable={fieldDisable}
          pastOnly
          />
      );
    case 'select':
      return wrap(
        <Select
          name={fieldName}
          onChange={e => onChange(e, fieldName)}
          value={getDisplayForValue(field.choices, value)}
          choices={field.choices}
          disable={fieldDisable}
          />
      );
    case 'selectmultiple':
      // TODO: tags select here
      return wrap(
        <input placeholder=">>Tag Select Goes Here<<"/>
      );
    case 'checkbox':
      return wrap(
        <CheckBox
          name={fieldName}
          onChange={e => onChange(e, fieldName)}
          required={field.required}
          initial={field.initial}
          maxLength={field.widget.maxlength}
          isHidden={field.widget.is_hidden}
          placeholder={field.widget.attrs.placeholder}
          autoFocus={field.widget.attrs.autofocus}
          disable={fieldDisable}
          />
      );
    default:
      warning(false, `Unknown field type for ${fieldName}: ${inputType}`);
      return <span/>;
    }
  }
}

RemoteFormField.propTypes = {
  form: PropTypes.object.isRequired,
  fieldName: PropTypes.string.isRequired,
  value: PropTypes.any.isRequired,
  onChange: PropTypes.func.isRequired,
};
