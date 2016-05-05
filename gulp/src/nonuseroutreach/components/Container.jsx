import React, {Component, PropTypes} from 'react';

import {Content} from './Content';
import {Menu} from './Menu';


// the "master" container
export class Container extends Component {
  constructor(props) {
    super(props);
    this.state = {
      page: 'Overview',
      tips: [],
    };
  }

  /**
   * change what is displayed in the "Content" div.
   *
   * option parameter "tips" allows a list of tips to display beneath
   * the navigation menu
   */
  changePage(page, tips = []) {
    this.setState({page, tips});
  }

  render() {
    const {page, tips} = this.state;
    const {recordsManager} = this.props;
    return (
      <div>
        <div className="row">
          <div className="col-sm-12">
            <div className="breadcrumbs">
              <span>
                Non-User Outreach Inbox Management
              </span>
            </div>
          </div>
        </div>

        <div className="row">
          <Content page={page} recordsManager={recordsManager} />
          <Menu changePage={(p, t) => this.changePage(p, t)} tips={tips} />
        </div>
        <div className="clearfix"></div>
      </div>
    );
  }
}

Container.propTypes = {
  inboxManager: PropTypes.object.isRequired,
  recordsManager: PropTypes.object.isRequired,
};
