import React, {Component, PropTypes} from 'react';
import {Router, Route, IndexRedirect} from 'react-router';
import {DynamicReportApp} from 'reporting/DynamicReportApp';
import SetUpReport from 'reporting/SetUpReport';

export class WizardRouter extends Component {
  createElement(TheComponent, componentProps) {
    const {reportFinder} = this.props;
    const newProps = {...componentProps, reportFinder};

    return <TheComponent {...newProps}/>;
  }

  render() {
    return (
      <Router createElement={(c, p) => this.createElement(c, p)}>
        <Route path="/" component={DynamicReportApp}>
          <IndexRedirect to="set-up-report"/>
          <Route
            path="set-up-report(/:dataType)"
            component={SetUpReport}/>
        </Route>
      </Router>
    );
  }
}

WizardRouter.propTypes = {
  reportFinder: PropTypes.object.isRequired,
};
