import {handleActions} from 'redux-actions';
import {validateEmail} from '../../common/email-validators';
import {difference} from 'lodash-compat';
import unionBy from 'lodash.unionby';

export const initialValidation = {
  email: {
    value: '',
    errors: [],
  },
  roles: {
    value: [],
    errors: [],
  },
};

export default handleActions({
  'VALIDATE_EMAIL': (state, action) => {
    const errors = validateEmail(action.payload) ? [] : [
      'Invalid email address',
    ];
    return {
      ...state,
      email: {
        value: action.payload,
        errors: errors,
      },
    };
  },
  'CLEAR_VALIDATION': () => initialValidation,
  'ADD_ROLES': (state, action) => {
    return {
      ...state,
      roles: {
        ...state.roles,
        value: unionBy(action.payload, state.roles.value, 'display'),
        errors: [],
      },
    };
  },
  'REMOVE_ROLES': (state, action) => {
    const roles = difference(state.roles.value, action.payload);
    return {
      ...state,
      roles: {
        ...state.roles,
        value: roles,
        // TODO: account for last admin
        errors: Object.keys(roles).length ? [] : [
          'A user must be assigned to at least one role.',
        ],
      },
    };
  },
}, initialValidation);
