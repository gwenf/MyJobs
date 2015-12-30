import React, {PropTypes, Component} from 'react';
import {SearchInput} from 'common/ui/SearchInput';


/**
 * Box of collected items with a search box for adding more.
 */
export class AddNewBox extends Component {
  constructor() {
    super();
    this.state = {
      showInput: false,
    };
  }

  onClick() {
    this.setState({showInput: true}, () => {
      const {suggest} = this.refs;
      suggest.focus();
    }, 300);
  }

  onSuggestBlur() {
    this.setState({showInput: false});
  }

  handleAddTag(t) {
    const {addTag} = this.props;
    this.setState({showInput: false});
    addTag(t);
  }

  render() {
    const {getHints} = this.props;
    const {showInput} = this.state;
    let contents;

    if (showInput) {
      contents = (
        <SearchInput
          ref="suggest"
          emptyOnSelect
          id="zzzzz"
          onSelect={t => this.handleAddTag(t)}
          getHints={v => getHints(v)}
          placeholder="Type item and hit Enter"
          onBlur={() => this.onSuggestBlur()}
          theme={{
            root: 'dropdown search',
            rootOpen: 'open',
            suggestions: 'dropdown-menu',
            input: 'search-input',
            itemActive: 'active',
          }}/>
      );
    } else {
      contents = (
        <div className="inside-bucket">
          <span className="bucket-text">
            Search, Drag, or Click for New
            <div className="bucket-icon-green">
              <i className="fa fa-plus-circle fa-2x"></i>
            </div>
          </span>
        </div>
      );
    }

    return (
      <div className="add-new-bucket" onClick={() => this.onClick() }>
        {contents}
      </div>
    );
  }
}

AddNewBox.propTypes = {
  /**
   * Id for wai-aria. See SearchInput.
   */
  id: PropTypes.string.isRequired,

  /**
   * Callback: the user has added a tag.
   *
   * key: key for the tag selected by the user.
   */
  addTag: PropTypes.func.isRequired,

  /**
   * Callback: the user wants hints for a given partial string.
   */
  getHints: PropTypes.func.isRequired,
};