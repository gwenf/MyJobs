import React, {PropTypes, Component} from 'react';
import {Loading} from 'common/ui/Loading';
import {LinkRow} from './LinkRow';

export class WizardPageReportingTypes extends Component {
  componentWillMount() {
    this.setState({
      loading: true,
    });
  }

  componentDidMount() {
    this.loadData();
  }

  async loadData() {
    const {reportFinder} = this.props;
    const reportingTypes = await reportFinder.getReportingTypes();
    this.setState({
      loading: false,
      data: reportingTypes,
    });
  }

  render() {
    const {loading, data} = this.state;

    let rows;
    if (loading) {
      rows = <Loading/>;
    } else {
      rows = Object.keys(data).map(k =>
        <LinkRow
          key={k}
          label={data[k].name}
          text={data[k].description}
          to={`/report-types/${k}`}/>
      );
    }

    return (
      <div>
        <div className="row">
          <div className="col-xs-12">
            <h4>Reporting Types</h4>
          </div>
        </div>
        {rows}
      </div>
    );
  }
}

WizardPageReportingTypes.propTypes = {
  reportFinder: PropTypes.object.isRequired,
};
