import React, {PropTypes, Component} from 'react';
import {AndOrContainer} from 'common/ui/tags/AndOrContainer';

export class WizardFilterTags extends Component {
  render() {
    const {tags, addTag, removeTag, getHints} = this.props;
    return (
      <AndOrContainer
        allItems={[]}
        andGroup={tags}
        addTag={addTag}
        removeTag={removeTag}
        getHints={getHints}/>
    );
  }
}

WizardFilterTags.propTypes = {
  tags: PropTypes.array.isRequired,
  addTag: PropTypes.func.isRequired,
  removeTag: PropTypes.func.isRequired,
  getHints: PropTypes.func.isRequired,
};
