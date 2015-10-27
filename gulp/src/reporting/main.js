import {bootstrap} from "./bootstrap.js";
import Api from './api';
import {getCsrf} from 'util/cookie';
import {initialState, ActionCreators, reduce} from './actions';
import {DynamicReportApp} from "./view.js";

import {createStore, applyMiddleware} from "redux";
import React from "react";
import ReactDOM from "react-dom";
import {Provider, connect} from "react-redux";

bootstrap();

const api = new Api(getCsrf());

const loggingMiddleware = store => next => action => {
    console.log("Dispatching action:", action.type, action);
    return next(action);
};

const store = applyMiddleware(loggingMiddleware)(createStore)(reduce, initialState);
window.store = store;

const creators = new ActionCreators(api, store.dispatch.bind(store));

// Hook react up to redux and start react.
var Connected = connect(s => ({...s, creators}))(DynamicReportApp);

ReactDOM.render(
    <div>
        <Provider store={store}>
            <Connected/>
        </Provider>
    </div>,
    // Where to put this application
    document.getElementById("reporting-app")
);

creators.reset();
