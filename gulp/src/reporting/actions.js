import Immutable from 'immutable';
import {get_csrf} from 'util/cookie.js';
import {registerAction} from './store.js';

var csrf = get_csrf();

// This is the last bit of jquery left, afaik. We should use the
// ES6 fetch polyfill instead.
function load(url, formData = {}) {
    var data = {...formData, csrfmiddlewaretoken: csrf};
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: url,
            type: "POST",
            dataType: "json",
            data: data,
            withCredentials: true,
        }).then(resolve, reject);
    });
}


// This is the view independent business logic of the application. It is
// critical that we like what we see here. I'm not entirely happy with it yet
// for a few reasons:
//
// * It more or less forms a state machine, which can be tough to follow. Can't
//   do too much about that.
// * It is heavily entangled with Facebook's Immutable library. That is a good
//   library but I'd rather write my business logic in JavaScript. The ES6 spread
//   operator provides an easy way to comply with the requirements of redux
//   reducers so it might be worth trying that. The ES6 spread operator is JS.
// * You _really_ have to understand how registerAction works to have any sense
//   of what is going on here. Splitting registerAction into syncronous and
//   async versions might help.

var Actions = {
    loadReportingTypes: registerAction('LOAD_REPORTING_TYPES',
        () => load("/reports/api/reporting_types"),
        function (state, payload) {
            var newState = state.set('reportingTypes',
                                     Immutable.fromJS(payload['reporting_type'])).
                           set('pageIndex', 'reportingTypes');
            return newState;
        },
        function(state, error) {
            return state.set('error', true);
        }),

    selectReportingType: registerAction('SELECT_REPORTING_TYPE',
        i => i,
        (s, p) => s.set('selectedReportingType', p)),

    loadReportTypes: registerAction('LOAD_REPORT_TYPES',
        (reportingType) => load("/reports/api/report_types",
                                {reporting_type_id: reportingType}),
        function (state, payload) {
            var newState = state.set('reportTypes',
                                     Immutable.fromJS(payload['report_type'])).
                           set('pageIndex', 'reportTypes');
            return newState;
        },
        function(state, error) {
            return state.set('error', true);
        }),

    selectReportType: registerAction('SELECT_REPORT_TYPE',
        i => i,
        (s, p) => s.set('selectedReportType', p)),

    loadDataTypes: registerAction('LOAD_DATA_TYPES',
        (reportType) => load("/reports/api/data_types",
                             {report_type_id: reportType}),
        function (state, payload) {
            var newState = state.set('dataTypes',
                                     Immutable.fromJS(payload['data_type'])).
                           set('pageIndex', 'dataTypes');
            return newState;
        },
        function(state, error) {
            return state.set('error', true);
        }),

    selectDataType: registerAction('SELECT_DATA_TYPE', i => i,
        (s, p) => s.set('selectedDataType', p)),

    loadPresentationTypes: registerAction('LOAD_PRESENTATION_TYPES',
        (reportType, dataType) => load("/reports/api/report_presentations",
                                        {data_type_id: dataType,
                                         report_type_id: reportType}),
        function (state, payload) {
            var newState = state.set('presentationTypes',
                                     Immutable.fromJS(payload['report_presentation'])).
                           set('pageIndex', 'presentationTypes');
            return newState;
        },
        function(state, error) {
            return state.set('error', true);
        }),

    selectPresentationType: registerAction('SELECT_PRESENTATION_TYPE',
        i => i,
        (s, p) => s.set('selectedPresentationType', p)),

    runReport: registerAction('RUN_REPORT',
        (reportPresentation) => load("/reports/api/run_report",
                                     {rp_id: reportPresentation}),
    function (state, payload) {
        var newState = state.update('reports', v => v.push(payload.id));
        return newState;
    },
    function (state, error) {
        return state.set('error', true);
    }),
};

export { Actions as default };

