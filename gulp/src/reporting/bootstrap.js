import {polyfill as es6PromisePolyfill} from 'es6-promise';
import 'fetch-polyfill';

// Put as many polyfills here as we can.
//
// ES5-shim/sham and babel/polyfill probably have to be part of the bundling
// environment.

export function bootstrap() {
    // This gives us the Promise API.
    es6PromisePolyfill();
}
