import React, {PropTypes, Component} from 'react';
import {Loading} from 'common/ui/Loading';
import {LinkRow} from './LinkRow';


export class WizardPageReportTypes extends Component {
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
    const {reportingType} = this.props.routeParams;
    const reportTypes = await reportFinder.getReportTypes(reportingType);
    this.setState({
      loading: false,
      data: reportTypes,
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
          to={`/data-types/${k}`}/>
      );
    }

    return (
      <div>
        <div className="row">
          <div className="col-xs-12">
            <h4>Report Types</h4>
          </div>
        </div>
        {rows}
      </div>
    );
  }
}

WizardPageReportTypes.propTypes = {
  routeParams: PropTypes.shape({
    reportingType: PropTypes.string.isRequired,
  }).isRequired,
  reportFinder: PropTypes.object.isRequired,
};
