import {bootstrap} from "./bootstrap.js";
import Actions from "./actions.js";
import {DynamicReportApp} from "./view.js";
import {store} from "./store.js";
import React from "react";
import ReactDOM from "react-dom";
import {Provider, connect} from "react-redux";

// This is the entry point of the application. Bundling begins here.

// Take care of fundamental browser stuff.
bootstrap();

// Hook react up to redux and start react.
var Connected = connect(s => s.toObject())(DynamicReportApp);

ReactDOM.render(
    <div>
        <Provider store={store}>
            <Connected/>
        </Provider>
    </div>,
    // Where to put this application
    document.getElementById("reporting-app")
);

// Kick off our redux application.
Actions.loadReportingTypes();

