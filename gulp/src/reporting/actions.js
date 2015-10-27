import {deepFreeze} from '../util/freeze';

export var initialState = deepFreeze({
    reportingTypes: {},
    selectedReportingType: null,

    reportTypes: {},
    selectedReportType: null,

    dataTypes: {},
    selectedDataType: null,

    presentationTypes: {},
    selectedPresentationType: null,

    pageIndex: 'reportingTypes',

    loading: false,

    error: "",
    reports: [],
});

export class ActionCreators {
    constructor(api, dispatch) {
        this.api = api;
        this.dispatch = dispatch;
    }

    async reset() {
        this.dispatch(Actions.loading(true));
        try {
            const rts = await this.api.getReportingTypes();
            this.dispatch(Actions.nextPage("reportingTypes", rts, "reportingTypes"));
        } catch(e) {
            console.error(e);
            console.error(e.stack);
            this.dispatch(Actions.unexpectedError("Error while getting reporting types."));
        }
    }

    async nextAfterReportingType(reportingTypeId) {
        try {
            this.dispatch(Actions.select("selectedReportingType", reportingTypeId));
            this.dispatch(Actions.loading(true));
            const rts = await this.api.getReportTypes(reportingTypeId)
            this.dispatch(Actions.nextPage("reportTypes", rts, "reportTypes"));
        } catch(e) {
            console.error(e.stack);
            this.dispatch(Actions.unexpectedError("Error while getting report types."));
        }
    }

    async nextAfterReportType(reportTypeId) {
        try {
            this.dispatch(Actions.select("selectedReportType", reportTypeId));
            this.dispatch(Actions.loading(true));
            const dts = await this.api.getDataTypes(reportTypeId)
            this.dispatch(Actions.nextPage("dataTypes", dts, "dataTypes"));
        } catch(e) {
            console.error(e.stack);
            this.dispatch(Actions.unexpectedError("Error while getting data types."));
        }
    }

    async nextAfterDataType(reportTypeId, dataTypeId) {
        try {
            this.dispatch(Actions.select("selectedDataType", dataTypeId));
            this.dispatch(Actions.loading(true));
            const dts = await this.api.getPresentationTypes(reportTypeId, dataTypeId)
            this.dispatch(Actions.nextPage("presentationTypes", dts, "presentationTypes"));
        } catch(e) {
            console.error(e.stack);
            this.dispatch(Actions.unexpectedError("Error while getting presentationTypes types."));
        }
    }

    async nextAfterPresentationType(reportPresentationId) {
        try {
            this.dispatch(Actions.select("selectedPresentationType", reportPresentationId));
            this.dispatch(Actions.loading(true));
            const report = await this.api.runReport(reportPresentationId)
            this.dispatch(Actions.receiveReport(report));
            return this.reset()
        } catch(e) {
            console.error(e.stack);
            this.dispatch(Actions.unexpectedError("Error while getting presentationTypes types."));
        }
    }
};

export const Actions = {
    loading: (val) => ({type: 'LOADING', loading: val}),
    select: (key, id) => ({type: 'SELECT', key: key, id: id}),
    nextPage: (dataKey, newData, newPage) =>
        ({
            type: 'NEXT_PAGE',
            dataKey: dataKey,
            newData: newData,
            newPage: newPage,
        }),
    receiveReport: (report) => ({type: 'REPORT', report: report}),
    unexpectedError: (message) => ({type: 'ERROR', message: message}),
};

export function reduce(state, action) {
    switch(action.type) {
        case 'NEXT_PAGE': {
            const {dataKey, newData, newPage} = action;
            const newState = {
                ...state,
                pageIndex: newPage,
                loading: false,
            };
            newState[dataKey] = newData;
            return Object.freeze(newState);
        }
        case 'SELECT': {
            const {key, id} = action;
            const newState = {...state};
            newState[key] = parseInt(id);
            return Object.freeze(newState);
        }
        case 'REPORT': {
            const {report} = action;
            const reportList = [report, ...state.reports];
            return Object.freeze({...state, reports: reportList});
        }
        case 'LOADING':
            return Object.freeze({...state, loading: action.loading});
        case 'ERROR':
            return Object.freeze({...state, error: action.message});
        default:
            return state;
    }
}
