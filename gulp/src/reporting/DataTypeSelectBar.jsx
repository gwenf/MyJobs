import React, {Component, PropTypes} from 'react';
import Select from 'common/ui/Select';
import {getDisplayForValue} from 'common/array';

export default class DataTypeSelectBar extends Component {
  render() {
    const {
      intentionChoices,
      intentionValue,
      onIntentionChange,
      categoryChoices,
      categoryValue,
      onCategoryChange,
      dataSetChoices,
      dataSetValue,
      onDataSetChange,
    } = this.props;

    return (
      <div className="row">
        <fieldset className="fieldset-border">
            <legend className="fieldset-border">Report Configuration</legend>
            <div className="col-xs-3">
              <label>Report Intention</label>
              <Select
                onChange={e => onIntentionChange(e.target.value)}
                choices = {intentionChoices}
                value = {
                  getDisplayForValue(intentionChoices, intentionValue)}
                name = ""
              />
            </div>
            <div className="col-xs-3">
              <label>Report Category</label>
              <Select
                onChange={e => onCategoryChange(e.target.value)}
                choices = {categoryChoices}
                value = {
                  getDisplayForValue(categoryChoices, categoryValue)}
                name = ""
              />
            </div>
            <div className="col-xs-6">
              <label>Data Set</label>
              <Select
                onChange={e => onDataSetChange(e.target.value)}
                choices = {dataSetChoices}
                value = {
                  getDisplayForValue(dataSetChoices, dataSetValue)}
                name = ""
              />
            </div>
        </fieldset>
      </div>
    );
  }
}

DataTypeSelectBar.propTypes = {
  intentionChoices: React.Proptypes.arrayOf(
    PropTypes.shape({
      value: React.Proptypes.any.isRequired,
      display: React.Proptypes.string.isRequired,
    })
  ),
  intentionValue: React.Proptypes.string.isRequired,
  onIntentionChange: React.Proptypes.func.isRequired,

  categoryChoices: React.Proptypes.arrayOf(
    PropTypes.shape({
      value: React.Proptypes.any.isRequired,
      display: React.Proptypes.string.isRequired,
    })
  ),
  categoryValue: React.Proptypes.string.isRequired,
  onCategoryChange: React.Proptypes.func.isRequired,
  dataSetChoices: React.Proptypes.arrayOf(
    PropTypes.shape({
      value: React.Proptypes.any.isRequired,
      display: React.Proptypes.string.isRequired,
    })
  ),
  dataSetValue: React.Proptypes.string.isRequired,
  onDataSetChange: React.Proptypes.func.isRequired,
};
