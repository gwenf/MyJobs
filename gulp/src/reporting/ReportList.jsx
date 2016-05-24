import React, {PropTypes, Component} from 'react';
import {map} from 'lodash-compat';
import {setCookie} from 'common/cookie';
import PopMenu from 'common/ui/PopMenu';
import classnames from 'classnames';

export class ReportList extends Component {
  constructor() {
    super();
    this.state = {
      currentlyActive: '',
      reportsRefreshing: [],
    };
  }

  clickMenu(e) {
    const {currentlyActive: oldActiveId} = this.state;
    const activeId = e.target.parentNode.parentNode.id;

    // Hide if they clicked the same one. Important for IE8.
    const currentlyActive = oldActiveId === activeId ? '' : activeId;
    this.setState({currentlyActive});
  }

  handleRefreshReport(report) {
    const {reportFinder} = this.props;
    const {reportsRefreshing} = this.state;
    const removeReport = () => {
      reportsRefreshing.splice(reportsRefreshing.indexOf(report.id), 1);
      this.setState({reportsRefreshing: reportsRefreshing});
    };
    if (reportsRefreshing.indexOf(report.id) === -1) {
      reportsRefreshing.push(report.id);
      this.setState({reportsRefreshing: reportsRefreshing});
      reportFinder.refreshReport(report.id).then(removeReport, removeReport);
    }
    this.closeAllPopups();
  }

  handlePreviewReport(report) {
    const {history} = this.props;
    const href = '/preview/' + report.id;
    const query = {
      reportName: report.name,
      reportType: report.report_type,
    };
    this.closeAllPopups();
    history.pushState(null, href, query);
  }

  handleExportReport(report) {
    const {history} = this.props;
    const href = '/export/' + report.id;
    this.closeAllPopups();
    history.pushState(null, href);
  }

  handleCreateNewReport(e) {
    const {history} = this.props;
    e.preventDefault();
    history.pushState(null, '/');
  }

  handleSwitchVersions() {
    setCookie('reporting_version', 'classic');
    window.location.assign('/reports/view/overview');
  }

  async handleCloneReport(report) {
    const {history, reportFinder} = this.props;
    const reportInfo = await reportFinder.getReportInfo(report.id);
    const href = '/set-up-report';
    const query = {
      reportDataId: reportInfo.report_data_id,
      intention: reportInfo.reporting_type,
      category: reportInfo.report_type,
      dataSet: reportInfo.data_type,
    };
    const newReportState = {
      ...reportInfo,
      name: 'Copy of ' + reportInfo.name,
    };
    history.pushState(newReportState, href, query);
  }

  closeAllPopups() {
    this.setState({currentlyActive: ''});
  }

  render() {
    const {reports, highlightId} = this.props;
    const {currentlyActive} = this.state;
    const reportLinks = map(reports, r => {
      const options = [];
      const numberedID = 'listentry' + r.id;
      let isThisMenuActive = false;
      if (numberedID === currentlyActive) {
        isThisMenuActive = true;
      }
      if (r.report_type && r.id) {
        options.push({
          display: 'Preview',
          onSelect: () => {this.handlePreviewReport(r);},
        });
      }
      if (r.id) {
        options.push({
          display: 'Export',
          onSelect: () => {this.handleExportReport(r);},
        }, {
          display: 'Refresh',
          onSelect: () => {this.handleRefreshReport(r);},
        });
        options.push({
          display: 'Clone',
          onSelect: () => {this.handleCloneReport(r);},
        });
      }
      return (
        <li
          className={classnames(
            highlightId === r.id ? 'active' : '',
            numberedID === currentlyActive ? 'active-parent' : '',
          )}
          key={r.id}
          id={numberedID}>
          {options.length > 0 ?
            <PopMenu options={options}
              isMenuActive={isThisMenuActive}
              toggleMenu={(e) => this.clickMenu(e)}
              closeAllPopups={(e) => this.closeAllPopups(e)} />
              : ''}
          {(r.isRunning || this.state.reportsRefreshing.indexOf(r.id) > -1) ?
            <span className="report-loader"></span>
            : ''}
          <span className="menu-text">{r.name}</span>
        </li>
      );
    });

    return (
      <div>
        <div className="sidebar reporting">
          <h2 className="top">Saved Reports</h2>
          <button
            className="button primary wide"
            onClick={e => this.handleCreateNewReport(e)}>
            Create a New Report
          </button>
          <div className="report-list">
            <ul>
              {reportLinks}
            </ul>
          </div>
          <h2>Reporting Version</h2>
          <button
            className="button primary wide"
            onClick={() => this.handleSwitchVersions()}>
            Switch to Classic Reporting
          </button>
        </div>
      </div>
    );
  }
}

ReportList.propTypes = {
  history: PropTypes.object.isRequired,
  reportFinder: PropTypes.object.isRequired,
  reports: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number,
      name: PropTypes.string.isRequired,
      report_type: PropTypes.string,
      isRunning: PropTypes.bool.isRequired,
    }),
  ).isRequired,
  highlightId: PropTypes.number,
};
