import React from 'react';
import FilteredMultiSelect from 'react-filtered-multiselect';

const bootstrapClasses = {
  filter: 'form-control',
  select: 'form-control',
  button: 'btn btn btn-block btn-default',
  buttonActive: 'btn btn btn-block btn-primary',
};

const ActivitiesMultiselect = React.createClass({
  propTypes: {
    availableActivities: React.PropTypes.array.isRequired,
    assignedActivities: React.PropTypes.array.isRequired,
  },
  getInitialState() {
    return {
      availableActivities: this.props.availableActivities,
      assignedActivities: this.props.assignedActivities,
    };
  },
  componentWillReceiveProps(nextProps) {
    this.setState({
      availableActivities: nextProps.availableActivities,
      assignedActivities: nextProps.assignedActivities,
    });
  },
  _onSelect(assignedActivities) {
    assignedActivities.sort((a, b) => a.id - b.id);
    this.setState({assignedActivities});
  },
  _onDeselect(deselectedOptions) {
    const assignedActivities = this.state.assignedActivities.slice();
    deselectedOptions.forEach(option => {
      assignedActivities.splice(assignedActivities.indexOf(option), 1);
    });
    this.setState({assignedActivities});
  },
  render() {
    const {assignedActivities, availableActivities} = this.state;

    return (
        <div className="row">

          <div className="col-xs-6">
            <label>Activities Available:</label>
            <FilteredMultiSelect
              buttonText="Add"
              classNames={bootstrapClasses}
              onChange={this._onSelect}
              options={availableActivities}
              selectedOptions={assignedActivities}
              textProp="name"
              valueProp="id"
            />
          </div>
          <div className="col-xs-6">
            <label>Activities Assigned:</label>
            <FilteredMultiSelect
              buttonText="Remove"
              classNames={{
                filter: 'form-control',
                select: 'form-control',
                button: 'btn btn btn-block btn-default',
                buttonActive: 'btn btn btn-block btn-danger',
              }}
              onChange={this._onDeselect}
              options={assignedActivities}
              textProp="name"
              valueProp="id"
            />
          </div>
        </div>
    );
  },
});

export default ActivitiesMultiselect;
