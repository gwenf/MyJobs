import React, {PropTypes, Component} from 'react';


export class WizardFilterDateRange extends Component {
    constructor() {
      super();
      this.state = {begin: '', end: ''};
    }

    updateField(field, value) {
      const {updateFilter} = this.props;
      const newState = {...this.state};
      newState[field] = value;
      this.setState(newState);
      updateFilter([newState.begin, newState.end]);
    }

    render() {
      return (
        <span>
          <div>
            <input
              type="text"
              placeholder="begin date"
              onChange={e =>
                this.updateField('begin', e.target.value)} />
          </div>
          <div style={{margin: '20px 0 0'}}>
            <input
              type="text"
              placeholder="end date"
              onChange={e =>
                this.updateField('end', e.target.value)} />
          </div>
        </span>
      );
    }

}

WizardFilterDateRange.propTypes = {
  id: PropTypes.string.isRequired,
  updateFilter: PropTypes.func.isRequired,
};
