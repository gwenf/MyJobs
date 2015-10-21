import Immutable from "immutable";
import {createStore, applyMiddleware} from "redux";
import {get_csrf} from "util/cookie.js";

// Most of this can be done with off-the-shelf middleware, such as
// redux-promise or redux-actions. Writing this turned out to be less
// headache at the time. (But at the time I was fighting with IE8 and
// ES6 module loading, so things might be different now.)

var localHandlers = {};
export var store = null;

//  Modelled remotely after redux-actions and redux-promise.
//
//  This mechanism allows the developer to define an action and it's associated
//  reducers all in one place.
//
//  arguments:
//      type: A string constant like 'DO_THING'. It will appear in logs.
//      meta: A filter function to call on the provied action payload.
//          examples:
//          If synchronous a good choice is identity: i => i
//          If async and no args are needed use () => doasyncthing()
//      next: success callback.
//          Called for synchronous actions and async success.
//          Function should be usable as a redux reducer. (state, action) => state
//      error: error callback
//          Called for async errors.
//          Function should be usable as a redux reducer. (state, error) => state
//  returns:
//      A function which can be called to dispatch this action. The signature
//      of the function depends on the signature of meta.
//      The arguments to this dispatcher function are passed through meta
//      before being sent to redux.
//      If the resulting argument is a promse, it is resolved before being sent.
//
//  future:
//      Break this function into registerAction and registerAsyncAction.

export function registerAction(type, meta, next, error = null) {
    if (error) {
        localHandlers[type] = function(state, action) {
            if('payload' in action) {
                return next(state, action.payload);
            } else {
                return error(state, action.error);
            }
        };
    } else {
        localHandlers[type] = function(state, action) {
            if('payload' in action) {
                return next(state, action.payload);
            } else {
                throw action.error;
            }
        }
    }
    return (...args) =>
        Promise.resolve(meta(...args))
            .then((p) => store.dispatch({type: type, payload: p}),
                  (e) => store.dispatch({type: type, error: e}));

}

// This really should be somewhere else. actions.js would be ideal but that
// would create a circular dependency between it and this module.
var initialState = Immutable.fromJS({
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

    error: false,
    reports: [],
});

function handleWithLocalHandlers(state = initialState, action) {
    console.log("handling action", action);
    if (action.type in localHandlers) {
        var newState = localHandlers[action.type](state, action);
        return newState;
    } else {
        return state;
    }
}

store = createStore(handleWithLocalHandlers);

