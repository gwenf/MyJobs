import {Actions, reduce, ActionCreators} from '../actions';
import {createStore} from 'redux';

import {promiseTest} from '../../util/spec';

describe("The reporting store reducer", () => {
    // Since state always changes in these tests, we can check some invariants
    // on every call.
    var reduceAndCheck = (origState, ...args) => {
        origState['canary'] = 'canary';
        const newState = reduce(origState, ...args);
        expect(Object.isFrozen(newState))
            .toBeTruthy("new state not frozen");
        expect(origState).not.toBe(newState,
            "new state should have new identity");
        expect(newState.canary).toBeDefined(
            "reducer did not copy old state");
        return newState;
    };

    it("can mark state as loading", () => {
        const newState = reduceAndCheck(
            {loading: false},
            Actions.loading(true));
        expect(newState.loading).toBe(true);
    });

    it("can mark state as errored", () => {
        const newState = reduceAndCheck(
            {error: null},
            Actions.unexpectedError("E!"));
        expect(newState.error).toBe("E!");
    });

    it("can receive a report", () => {
        const newState = reduceAndCheck(
            {reports: [{id: 1}]},
            Actions.receiveReport({id: 2}));
        expect(newState.reports).toEqual([{id: 2}, {id: 1}]);
    });

    it("can store a selected item", () => {
        const newState = reduceAndCheck(
            {selectedDataType: null},
            Actions.select("selectedDataType", 22));
        expect(newState.selectedDataType).toBe(22);
    });

    it("can turn the page, and mark loading false", () => {
        const newState = reduceAndCheck(
            {pageIndex: "ZZ", loading: true},
            Actions.nextPage("someData", {a: 1}, "dataPage"));
        expect(newState.pageIndex).toBe("dataPage");
        expect(newState.loading).toBe(false);
        expect(newState.someData).toEqual({a: 1});
    });
});

describe("The action creator", () => {
    const fakeApi = {
        getReportingTypes: () => [1],
        getReportTypes: () => [2],
        getDataTypes: () => [3],
        getPresentationTypes: () => [4],
        runReport: () => ({id: 5}),
    };
    const actions = []
    const fakeDispatch = (a) => actions.push(a);
    const creators = new ActionCreators(fakeApi, fakeDispatch);

    const actionByType = (t) => actions.find((a) => a.type === t);

    beforeEach(() => actions.length = 0);

    it("can reset the wizard to reporting types", promiseTest(async () => {
        spyOn(fakeApi, 'getReportingTypes').and.callThrough();

        await creators.reset();

        expect(fakeApi.getReportingTypes).toHaveBeenCalled();
        const action = actionByType('NEXT_PAGE');
        expect(action).toEqual({
            type: 'NEXT_PAGE',
            dataKey: 'reportingTypes',
            newData: [1],
            newPage: 'reportingTypes',
        });
    }));

    it("can move next after reporting type", promiseTest(async () => {
        spyOn(fakeApi, 'getReportTypes').and.callThrough();

        await creators.nextAfterReportingType(33);

        expect(fakeApi.getReportTypes).toHaveBeenCalled();
        const pageAction = actionByType('NEXT_PAGE');
        expect(pageAction).toEqual({
            type: 'NEXT_PAGE',
            dataKey: 'reportTypes',
            newData: [2],
            newPage: 'reportTypes',
        });
        const selectAction = actionByType('SELECT');
        expect(selectAction).toEqual({
            type: 'SELECT',
            key: 'selectedReportingType',
            id: 33,
        });
    }));

    it("can move next after report type", promiseTest(async () => {
        spyOn(fakeApi, 'getDataTypes').and.callThrough();

        await creators.nextAfterReportType(44);

        expect(fakeApi.getDataTypes).toHaveBeenCalled();
        const pageAction = actionByType('NEXT_PAGE');
        expect(pageAction).toEqual({
            type: 'NEXT_PAGE',
            dataKey: 'dataTypes',
            newData: [3],
            newPage: 'dataTypes',
        });
        const selectAction = actionByType('SELECT');
        expect(selectAction).toEqual({
            type: 'SELECT',
            key: 'selectedReportType',
            id: 44,
        });
    }));

    it("can move next after data type", promiseTest(async () => {
        spyOn(fakeApi, 'getPresentationTypes').and.callThrough();

        await creators.nextAfterDataType(55, 66);

        expect(fakeApi.getPresentationTypes).toHaveBeenCalled();
        const pageAction = actionByType('NEXT_PAGE');
        expect(pageAction).toEqual({
            type: 'NEXT_PAGE',
            dataKey: 'presentationTypes',
            newData: [4],
            newPage: 'presentationTypes',
        });
        const selectAction = actionByType('SELECT');
        expect(selectAction).toEqual({
            type: 'SELECT',
            key: 'selectedDataType',
            id: 66,
        });
    }));

    it("can move next after presentation type", promiseTest(async () => {
        spyOn(fakeApi, 'runReport').and.callThrough();

        await creators.nextAfterPresentationType(55);

        expect(fakeApi.runReport).toHaveBeenCalled();
        const reportAction = actionByType('REPORT');
        expect(reportAction).toEqual({
            type: 'REPORT',
            report: {id: 5},
        });
    }));
});

