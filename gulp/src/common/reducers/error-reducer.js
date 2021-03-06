import {handleActions} from 'redux-actions';
import {groupBy} from 'lodash-compat/collection';
import {assign} from 'lodash-compat/object';


const defaultState = {currentErrors: {}};


/**
 *  errors format: {
 *    lastMessage: last exception message found
 *    currentErrors: error data accumulated from previous exceptions if any [
 *      {
 *        field: string name of a field to associated with this error;
 *          may be undefined.
 *        message: string message to show the user.
 *      }
 *    ]
 *  }
 */
export default handleActions({
  'ERROR': (state, action) => {
    const {message, data} = action.payload;
    const currentData = state.data || {};
    const indexedData = groupBy(data, o => o.field);
    const mergedData = assign({}, currentData, indexedData,
        (a, b) => (a || []).concat(b));
    return {
      lastMessage: message,
      currentErrors: mergedData,
    };
  },

  'CLEAR_ERRORS': () => {
    return defaultState;
  },
}, defaultState);
