import {handleActions} from 'redux-actions';
import {isEmpty, get} from 'lodash-compat';

const defaultState = {
  record: {
    partner: {},
    contacts: [],
    communication_record: {},
  },
};

/**
 * Represents the state of processing an NUO outreach record. {
 *
 *  state: string constant, What the user is doing right now.
 *    SELECT_PARTNER: the user is selecting a partner (or contact)
 *    NEW_PARTNER: the user is editing a new partner
 *    SELECT_CONTACT: the user is selecting a contact AFTER selecting a partner
 *    NEW_CONTACT: the user is editng a new contact
 *    CONTACT_APPEND: the user is adding notes to an existing contact
 *    NEW_COMMUNICATIONRECORD: the user is editing the new record
 *    SELECT_WORKFLOW_STATE: the user is picking the new workflow state
 *
 *  outreach: information for the current outreach record
 *  workflowStates: list of known workflow states {value:.., display:..}
 *  contactIndex: if editing a contact, which one is the user concerned with?
 *  blankForms: form data from Django defining available form fields.
 *  forms: form data from Django defining state of entered data, errors, etc.
 *  record: The record which will be submitted {
 *    outreachrecord: the outreach record we are working on
 *    partner: field contents for new partner
 *    contacts: [{ field contents for new contacts}]
 *    communication_record: field contents for record
 *  }
 */
export default handleActions({
  'NUO_RESET_PROCESS': (state, action) => {
    const {
      outreach,
      blankForms,
    } = action.payload;

    return {
      ...defaultState,
      state: 'SELECT_PARTNER',
      blankForms,
      forms: {
        contacts: [],
      },
      outreach,
    };
  },

  'NUO_DETERMINE_STATE': (state) => {
    let currentState;
    let newForms = state.forms;
    if (isEmpty(state.record.partner)) {
      currentState = 'SELECT_PARTNER';
    } else if (isEmpty(state.record.contacts)) {
      currentState = 'SELECT_CONTACT';
    } else if (isEmpty(state.record.communication_record)) {
      currentState = 'NEW_COMMUNICATIONRECORD';
      newForms = {
        ...state.forms,
        communication_record: state.blankForms.communication_record,
      };
    } else {
      currentState = 'SELECT_WORKFLOW_STATE';
    }
    return {
      ...state,
      state: currentState,
      forms: newForms,
    };
  },

  'NUO_CHOOSE_PARTNER': (state, action) => {
    const {name, partnerId} = action.payload;

    return {
      ...state,
      record: {
        ...state.record,
        partner: {
          pk: partnerId,
          name: name,
        },
      },
    };
  },

  'NUO_CHOOSE_CONTACT': (state, action) => {
    const {name, contactId} = action.payload;

    return {
      ...state,
      forms: {
        ...state.forms,
        contacts: [
          ...state.forms.contacts,
          null,
        ],
      },
      record: {
        ...state.record,
        contacts: [
          ...state.record.contacts,
          {
            pk: contactId,
            name: name,
          },
        ],
      },
    };
  },

  'NUO_NEW_PARTNER': (state, action) => {
    const {partnerName} = action.payload;

    const newState = {
      ...state,
      state: 'NEW_PARTNER',
      forms: {
        ...state.forms,
        partner: state.blankForms.partner,
      },
      record: {
        ...state.record,
        partner: {
          pk: '',
          name: partnerName,
        },
      },
    };

    delete newState.contactId;
    delete newState.contact;

    return newState;
  },

  'NUO_NEW_CONTACT': (state, action) => {
    const {contactName} = action.payload;
    const {contacts} = state.record;
    const newIndex = contacts.length;

    const newState = {
      ...state,
      state: 'NEW_CONTACT',
      contactIndex: newIndex,
      forms: {
        ...state.forms,
        contacts: [
          ...state.forms.contacts,
          state.blankForms.contact,
        ],
      },
      record: {
        ...state.record,
        contacts: [
          ...state.record.contacts,
          {
            pk: '',
            name: contactName,
          },
        ],
      },
    };

    return newState;
  },

  'NUO_EDIT_PARTNER': (state) => {
    return {
      ...state,
      state: 'NEW_PARTNER',
    };
  },

  'NUO_EDIT_CONTACT': (state, action) => {
    const {contactIndex} = action.payload;

    const pk = get(state, ['record', 'contacts', contactIndex, 'pk']);
    const newState = pk ? 'CONTACT_APPEND' : 'NEW_CONTACT';
    return {
      ...state,
      state: newState,
      contactIndex,
    };
  },

  'NUO_EDIT_COMMUNICATIONRECORD': (state) => {
    return {
      ...state,
      state: 'NEW_COMMUNICATIONRECORD',
    };
  },

  'NUO_DELETE_PARTNER': (state) => {
    // filter out contacts with a PK (i.e. existing contacts that would be
    // linked to the soon-to-be-removed parter
    const newContacts = state.record.contacts.filter(contact => !contact.pk);
    return {
      ...state,
      record: {
        ...state.record,
        partner: {},
        contacts: newContacts,
      },
    };
  },

  'NUO_DELETE_CONTACT': (state, action) => {
    const {contactIndex} = action.payload;
    const splicedContacts = state.record.contacts.slice();
    splicedContacts.splice(contactIndex, 1);

    return {
      ...state,
      record: {
        ...state.record,
        contacts: splicedContacts,
      },
    };
  },


  'NUO_DELETE_COMMUNICATIONRECORD': (state) => {
    return {
      ...state,
      record: {
        ...state.record,
        communication_record: {},
      },
    };
  },

  'NUO_RECEIVE_FORM': (state, action) => {
    const {form} = action.payload;

    return {
      ...state,
      form,
    };
  },

  'NUO_EDIT_FORM': (state, action) => {
    const {form: formName, formIndex, field, value} = action.payload;

    if (formIndex || formIndex === 0) {
      const formSet = (state.record || {})[formName] || [];
      const form = formSet[formIndex] || {};

      const newForm = {
        ...form,
        [field]: value,
      };

      const newFormSet = [...formSet];
      newFormSet[formIndex] = newForm;

      return {
        ...state,
        record: {
          ...state.record,
          [formName]: newFormSet,
        },
      };
    }

    const form = (state.record || {})[formName] || {};

    return {
      ...state,
      record: {
        ...state.record,
        [formName]: {
          ...form,
          [field]: value,
        },
      },
    };
  },

  'NUO_NOTE_FORMS': (state, action) => {
    const {record, forms} = action.payload;

    return {
      ...state,
      forms,
      record,
    };
  },
}, defaultState);
