import React, {PropTypes, Component} from 'react';
import {Loading} from 'common/ui/Loading';
import {LinkRow} from './LinkRow';


export class WizardPageDataTypes extends Component {
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
    const {reportType} = this.props.routeParams;
    const dataTypes = await reportFinder.getDataTypes(reportType);
    this.setState({
      loading: false,
      data: dataTypes,
    });
  }

  render() {
    const {loading, data} = this.state;
    const {reportType} = this.props.routeParams;

    let rows;
    if (loading) {
      rows = <Loading/>;
    } else {
      rows = Object.keys(data).map(k =>
        <LinkRow
          key={k}
          label={data[k].name}
          text={data[k].description}
          to={`/presentation-types/${reportType}/${k}`}/>
      );
    }

    return (
      <div>
        <div className="row">
          <div className="col-xs-12">
            <h4>Data Types</h4>
          </div>
        </div>
        {rows}
      </div>
    );
  }
}

WizardPageDataTypes.propTypes = {
  routeParams: PropTypes.shape({
    reportType: PropTypes.string.isRequired,
  }).isRequired,
  reportFinder: PropTypes.object.isRequired,
};
