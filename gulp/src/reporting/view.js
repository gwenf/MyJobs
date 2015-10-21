import Actions from './actions.js'
import React from 'react';

// Most of this is simple and self explanatory.
// DyanamicReportApp below is "smart" and controls what is seen when.

var Link = React.createClass({
    onClick() {
        this.props.onClick(this.props.id);
    },

    render() {
        return (
            <a className="" href="#" onClick={this.onClick}>
                {this.props.label}
            </a>
        );
    }
});

var LinkRow = React.createClass({
    onClick() {
        this.props.onClick(this.props.id);
    },

    render() {
        return (
            <div className="row">
                <div className="span3" style={ {textAlign: "right"}}>
                    <Link onClick={this.onClick} label={this.props.buttonText}/>
                </div>
                <div className="span4">{this.props.text}</div>
            </div>
        );
    }
});

var WizardPageReportingTypes = React.createClass({
    setReportingType(key) {
        Actions.selectReportingType(key);
        Actions.loadReportTypes(key);
    },

    render() {
        var data = this.props.data;
        var rows = data.entrySeq().map(e =>
            <LinkRow key={e[0]} id={e[0]} buttonText={e[1].get('name')}
                       text={e[1].get('description')}
                       onClick={this.setReportingType}/>
        ).toArray();

        return (
            <div>
                <div className="row">
                    <div className="span3" style={ {textAlign: "right"}}>
                    </div>
                    <div className="span4">
                        <h4>Reporting Types</h4>
                    </div>
                </div>
                {rows}
            </div>
        );
    },
});

var WizardPageReportTypes = React.createClass({
    setReportType(key) {
        Actions.selectReportType(key);
        Actions.loadDataTypes(key);
    },

    render() {
        var data = this.props.data;
        var rows = data.entrySeq().map(e =>
            <LinkRow key={e[0]} id={e[0]} buttonText={e[1].get('name')}
                       text={e[1].get('description')}
                       onClick={this.setReportType}/>
        ).toArray();

        return (
            <div>
                <div className="row">
                    <div className="span3" style={ {textAlign: "right"}}>
                    </div>
                    <div className="span4">
                        <h4>Report Types</h4>
                    </div>
                </div>
                {rows}
            </div>
        );
    },
});

var WizardPageDataTypes = React.createClass({
    setDataType(key) {
        Actions.selectDataType(key);
        Actions.loadPresentationTypes(this.props.reportType, key);
    },

    render() {
        var data = this.props.data;
        var rows = data.entrySeq().map(e =>
            <LinkRow key={e[0]} id={e[0]} buttonText={e[1].get('name')}
                       text={e[1].get('description')}
                       onClick={this.setDataType}/>
        ).toArray();

        return (
            <div>
                <div className="row">
                    <div className="span3" style={ {textAlign: "right"}}>
                    </div>
                    <div className="span4">
                        <h4>Data Types</h4>
                    </div>
                </div>
                {rows}
            </div>
        );
    },
});

var WizardPagePresentationTypes = React.createClass({
    setPresentationType(key) {
        Actions.selectPresentationType(key);
        Actions.runReport(key);
    },

    render() {
        var data = this.props.data;
        var rows = data.entrySeq().map(e =>
            <div key={e[0]} className="row">
                <div className="span3" style={ {textAlign: "right"}}>
                </div>
                <div className="span4">
                    <Link id={e[0]} label={e[1].get('name')}
                        onClick={this.setPresentationType}/>
                </div>
            </div>
        ).toArray();

        return (
            <div>
                <div className="row">
                    <div className="span3" style={ {textAlign: "right"}}>
                    </div>
                    <div className="span4">
                        <h4>Presentation Types</h4>
                    </div>
                </div>
                {rows}
            </div>
        );
    },
});

var ReportList = React.createClass({
    render() {
        var reportData = this.props.reports.map(reportId => ({
            id: reportId,
            href: "/reports/view/dynamicdownload?id=" + reportId
        }));
        var reportLinks = reportData.map(r =>
            <li key={r.id}>
                <a href={r.href}>Report id: {r.id}</a>
            </li>
        );

        return (
            <div>
                <div className="sidebar">
                    <h2 className="top">Reports</h2>
                    {reportLinks}
                </div>
            </div>
        );
    }

});

// Props for this component come directly from the store state. (see main.js).
export var DynamicReportApp = React.createClass({
    render: function() {
        var page;
        if (this.props.error) {
            page = <div><h3>Error!</h3></div>;
        } else {
            switch(this.props.pageIndex) {
                case "reportingTypes":
                    page =
                        <WizardPageReportingTypes data={this.props.reportingTypes}/>;
                    break;
                case "reportTypes":
                    page =
                        <WizardPageReportTypes data={this.props.reportTypes}/>;
                    break;
                case "dataTypes":
                    page =
                        <WizardPageDataTypes data={this.props.dataTypes}
                            reportType={this.props.selectedReportType}/>;
                    break;
                case "presentationTypes":
                    page =
                        <WizardPagePresentationTypes
                            data={this.props.presentationTypes}/>
                    break;
                default:
                    page = null;
            }
        }

        return (
            <div className="container">
                <div className="row">
                    <div className="span8 panel">
                        {page}
                    </div>
                    <div className="span4">
                        <ReportList reports={this.props.reports}/>
                    </div>
                </div>
            </div>
        );
    },
});

