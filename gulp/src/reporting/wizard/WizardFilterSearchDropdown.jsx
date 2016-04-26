import React, {PropTypes, Component} from 'react';
import {SearchInput} from 'common/ui/SearchInput';


export class WizardFilterSearchDropdown extends Component {
  onSearchSelect(value) {
    const {updateFilter} = this.props;
    updateFilter(value.key);
  }

  async getHints(input) {
    const {getHints} = this.props;
    const hints = await getHints(input);
    return hints;
  }

  render() {
    const {id, placeholder} = this.props;
    const eid = 'filter-autosuggest-' + id;

    return (
      <SearchInput
        id={eid}
        callSelectWhenEmpty
        placeholder={placeholder}
        onSelect={v => this.onSearchSelect(v)}
        getHints={p => this.getHints(p)}/>
    );
  }
}

WizardFilterSearchDropdown.propTypes = {
  id: React.Proptypes.string.isRequired,
  updateFilter: React.Proptypes.func.isRequired,
  getHints: React.Proptypes.func.isRequired,
  placeholder: React.Proptypes.string,
};
