import React, {PropTypes, Component} from 'react';
import {SearchInput} from 'common/ui/SearchInput';


export class WizardFilterCityState extends Component {
    constructor() {
      super();
      this.state = {city: '', state: ''};
    }

    updateField(field, value) {
      const {updateFilter} = this.props;

      // Update parent
      const newFilter = {...this.state};
      newFilter[field] = value.key;
      updateFilter(newFilter);

      // Set internal state
      const newState = {};
      newState[field] = value.key;
      this.setState(newState);
    }

    render() {
      const {id, getHints} = this.props;
      return (
        <span>
          <SearchInput
            id={id + '-city'}
            callSelectWhenEmpty
            placeholder="city"
            onSelect={v =>
              this.updateField('city', v)}
            getHints={v =>
              getHints('city', v)}/>
          <SearchInput
            id={id + '-state'}
            callSelectWhenEmpty
            placeholder="state"
            onSelect={v =>
              this.updateField('state', v)}
            getHints={v =>
              getHints('state', v)}/>
        </span>
      );
    }

}

WizardFilterCityState.propTypes = {
  id: PropTypes.string.isRequired,
  updateFilter: PropTypes.func.isRequired,
  getHints: PropTypes.func.isRequired,
};
