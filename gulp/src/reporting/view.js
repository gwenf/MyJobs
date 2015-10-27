import Actions from './actions.js'
import React, {PropTypes, Component} from 'react';

// Since we are using redux we can there is no need for this.state
// in components.

// DyanamicReportApp below is "smart" and controls what is seen when.

// Use ES6 class style for components that need handler methods.
// Also set up propTypes. They are a little tedious to type it but save time
// overall.
class Link extends Component {
    linkClick(e) {
        e.preventDefault();
        this.props.linkClick();
    }

    render() {
        return (
            <a className="" href="#" onClick={e => this.linkClick(e)}>
                {this.props.label}
            </a>
        );
    }
}

Link.propTypes = {
    linkClick: PropTypes.func.isRequired,
    label: PropTypes.string.isRequired,
};


// If a component is just a render method and a return statement use this form.
const LinkRow = (props) =>
    <div className="row">
        <div className="span3" style={{textAlign: "right"}}>
            <Link
                linkClick={() => props.linkClick(props.id)}
                label={props.buttonText}/>
        </div>
        <div className="span4">{props.text}</div>
    </div>;

LinkRow.propTypes = {
    linkClick: PropTypes.func.isRequired,
    text: PropTypes.string.isRequired,
    buttonText: PropTypes.string.isRequired,
};


// When defining a component with just a render method but you want to write
// javascript statements, use this function form.
const WizardPageReportingTypes = function(props) {
    const data = props.data;
    const rows = Object.keys(data).map(k =>
        <LinkRow key={k} id={k} buttonText={data[k]['name']}
            text={data[k]['description']}
            linkClick={() => props.creators.nextAfterReportingType(k)}/>
    );

    return (
        <div>
            <div className="row">
                <div className="span3" style={{textAlign: "right"}}>
                </div>
                <div className="span4">
                    <h4>Reporting Types</h4>
                </div>
            </div>
            {rows}
        </div>
    );
}

WizardPageReportingTypes.propTypes = {
    data: PropTypes.object.isRequired,
    creators: PropTypes.object.isRequired,
};


const WizardPageReportTypes = function(props) {
    const data = props.data;
    const rows = Object.keys(data).map(k =>
        <LinkRow key={k} id={k} buttonText={data[k]['name']}
            text={data[k]['description']}
            linkClick={() => props.creators.nextAfterReportType(k)}/>
    );

    return (
        <div>
            <div className="row">
                <div className="span3" style={{textAlign: "right"}}>
                </div>
                <div className="span4">
                    <h4>Report Types</h4>
                </div>
            </div>
            {rows}
        </div>
    );
}

WizardPageReportTypes.propTypes = {
    data: PropTypes.object.isRequired,
    creators: PropTypes.object.isRequired,
};


const WizardPageDataTypes = function(props) {
    const data = props.data;
    const rows = Object.keys(data).map(k =>
        <LinkRow key={k} id={k} buttonText={data[k]['name']}
            text={data[k]['description']}
            linkClick={() => props.creators.nextAfterDataType(props.reportType, k)}/>
    );

    return (
        <div>
            <div className="row">
                <div className="span3" style={{textAlign: "right"}}>
                </div>
                <div className="span4">
                    <h4>Data Types</h4>
                </div>
            </div>
            {rows}
        </div>
    );
}

WizardPageDataTypes.propTypes = {
    data: PropTypes.object.isRequired,
    reportType: PropTypes.number.isRequired,
    creators: PropTypes.object.isRequired,
};


const WizardPagePresentationTypes = function(props) {
    const data = props.data;
    const rows = Object.keys(data).map(k =>
        <div key={k} className="row">
            <div className="span3" style={{textAlign: "right"}}>
            </div>
            <div className="span4">
                <Link id={k} label={data[k]['name']}
                    linkClick={() => props.creators.nextAfterPresentationType(k)}/>
            </div>
        </div>
    );

    return (
        <div>
            <div className="row">
                <div className="span3" style={{textAlign: "right"}}>
                </div>
                <div className="span4">
                    <h4>Presentation Types</h4>
                </div>
            </div>
            {rows}
        </div>
    );
}

WizardPagePresentationTypes.propTypes = {
    data: PropTypes.object.isRequired,
    creators: PropTypes.object.isRequired,
};

const ReportList = function(props) {
    const reportData = props.reports.map(report => ({
        id: report.id,
        href: "/reports/view/dynamicdownload?id=" + report.id
    }));
    const reportLinks = reportData.map(r =>
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

ReportList.propTypes = {
    reports: PropTypes.arrayOf(PropTypes.object).isRequired,
};


// Props for this component come directly from the store state. (see main.js).
export const DynamicReportApp = function(props) {
    var page;
    if (props.error) {
        page = <div><h3>Error!</h3></div>;
    } else {
        switch(props.pageIndex) {
            case "reportingTypes":
                page =
                    <WizardPageReportingTypes
                        creators={props.creators}
                        data={props.reportingTypes}/>;
                break;
            case "reportTypes":
                page =
                    <WizardPageReportTypes
                        creators={props.creators}
                        data={props.reportTypes}/>;
                break;
            case "dataTypes":
                page =
                    <WizardPageDataTypes
                        creators={props.creators}
                        data={props.dataTypes}
                        reportType={props.selectedReportType}/>;
                break;
            case "presentationTypes":
                page =
                    <WizardPagePresentationTypes
                        creators={props.creators}
                        data={props.presentationTypes}/>
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
                    <ReportList reports={props.reports}/>
                </div>
            </div>
        </div>
    );
}

DynamicReportApp.propTypes = {
    creators: PropTypes.object.isRequired,
    reportingTypes: PropTypes.object.isRequired,
    selectedReportingType: PropTypes.number,

    reportTypes: PropTypes.object.isRequired,
    selectedReportType: PropTypes.number,

    dataTypes: PropTypes.object.isRequired,
    selectedDataType: PropTypes.number,

    presentationTypes: PropTypes.object.isRequired,
    selectedPresentationType: PropTypes.number,

    pageIndex: PropTypes.string.isRequired,

    loading: PropTypes.bool.isRequired,

    error: PropTypes.string.isRequired,
    reports: PropTypes.arrayOf(PropTypes.object).isRequired,

}
