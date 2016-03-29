import React, {PropTypes, Component} from 'react';
import {Loading} from 'common/ui/Loading';
import {Link} from 'react-router';


export class WizardPagePresentationTypes extends Component {
  constructor() {
    super();
    this.state = {
      loading: true,
    };
  }

  componentDidMount() {
    this.loadData();
  }

  async loadData() {
    const {reportFinder} = this.props;
    const {reportType, dataType} = this.props.routeParams;
    const reportTypes = await reportFinder.getPresentationTypes(
      reportType, dataType);
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
        <div key={k} className="row">
          <div className="col-xs-12">
            <Link
              to={`/set-up-report/${k}`}>
              {data[k].name}
            </Link>
          </div>
        </div>
      );
    }

    return (
      <div>
        <div className="row">
          <div className="col-xs-12">
            <h4>Presentation Types</h4>
          </div>
        </div>
        {rows}
      </div>
    );
  }
}

WizardPagePresentationTypes.propTypes = {
  routeParams: PropTypes.shape({
    reportType: PropTypes.string.isRequired,
    dataType: PropTypes.string.isRequired,
  }).isRequired,
  reportFinder: PropTypes.object.isRequired,
};
