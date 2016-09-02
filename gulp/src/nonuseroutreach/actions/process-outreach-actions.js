import {createAction} from 'redux-actions';
import {errorAction} from '../../common/actions/error-actions';
import {
  map,
  get,
  flatten,
  assign,
  omit,
  mapValues,
  isPlainObject,
  isEmpty,
  isUndefined,
} from 'lodash-compat';

/**
 *  Determine what the state of the process view should be
 */
export const determineProcessStateAction =
  createAction('NUO_DETERMINE_STATE');

/**
 * We have a new search field or we are starting over.
 */
export const resetProcessAction = createAction('NUO_RESET_PROCESS',
  (outreach, blankForms) =>
    ({outreach, blankForms}));

/**
 * Use chose a partner.
 *
 *  partnerId: database id of partner
 *  partner: partner data
 */
export const choosePartnerAction = createAction('NUO_CHOOSE_PARTNER',
    (partnerId, name) => ({partnerId, name}));

/**
 * Use chose a contact.
 *
 *  contactId: database id of contact
 *  contact: contact data
 */
export const chooseContactAction = createAction('NUO_CHOOSE_CONTACT',
    (contactId, name) => ({contactId, name}));

/**
 * Use chose to create a new partner
 *
 *  partnerName: Name chosen to start creating the new partner.
 */
export const newPartnerAction = createAction('NUO_NEW_PARTNER',
    (partnerName) => ({partnerName}));

/**
 * Use chose to create a new contact
 *
 *  contactName: Name chosen to start creating the new contact.
 */
export const newContactAction = createAction('NUO_NEW_CONTACT',
    (contactName) => ({contactName}));

/**
 * User wants to see a the new partner.
 */
export const editPartnerAction = createAction('NUO_EDIT_PARTNER');

/**
 * User wants to see a new contact.
 *
 * contactIndex: which one
 */
export const editContactAction = createAction('NUO_EDIT_CONTACT',
  contactIndex => ({contactIndex}));

/**
 * User wants to see the new communication record.
 */
export const editCommunicationRecordAction =
  createAction('NUO_EDIT_COMMUNICATIONRECORD');

/**
 * User wants to remove partner from the record
 */
export const deletePartnerAction = createAction('NUO_DELETE_PARTNER');

/**
 * User wants to remove contact from the record
 *
 * contactIndex: which one
 */
export const deleteContactAction = createAction('NUO_DELETE_CONTACT',
  contactIndex => ({contactIndex}));

/**
 * User wants to remove the communication record object
 */

export const deleteCommunicationRecordAction =
  createAction('NUO_DELETE_COMMUNICATIONRECORD');

/**
 * User edited a form.
 *
 * form: Which form the user edited, e.g. partner, contact, communciationrecord
 * field: field name, e.g. name, address, etc.
 * value: new value for the form field.
 * formIndex: For contact, an index to the form.
 */
export const editFormAction = createAction('NUO_EDIT_FORM',
  (form, field, value, formIndex) => ({form, field, value, formIndex}));

/**
 * convert an outreach record to have more js friendly keys
 *
 * record: record from api
 *
 * returns: the same record with friendlier keys.
 */
export function convertOutreach(record) {
  return {
    dateAdded: record.date_added,
    outreachBody: record.email_body,
    outreachFrom: record.from_email,
    outreachInbox: record.outreach_email,
    workflowState: record.current_workflow_state,
    outreachSubject: record.subject,
  };
}

/**
 * We have new form data from the API
 *
 * forms: new forms from the API
 */
export const noteFormsAction = createAction('NUO_NOTE_FORMS');

/**
 * Start the process by loading an outreach record and workflow states.
 *
 * outreachId: id for the outreach to load.
 */
export function doLoadEmail(outreachId) {
  return async (dispatch, getState, {api}) => {
    try {
      const outreach = await api.getOutreach(outreachId);
      const forms = await api.getForms();

      dispatch(
        resetProcessAction(
          convertOutreach(outreach),
          forms));
      dispatch(editFormAction('outreach_record', 'pk', outreachId, null));
    } catch (e) {
      dispatch(errorAction(e.message));
    }
  };
}

/**
 * Prepare an api forms object for merging with local record object.
 */
function formsFromApi(response) {
  const result = {
    forms: {},
    record: {},
  };

  const forms = response.forms;

  if (forms.outreach_record) {
    result.forms.outreach_record = forms.outreach_record;
    result.record.outreach_record = forms.outreach_record.data;
  }

  if (forms.partner) {
    result.forms.partner = forms.partner;
    result.record.partner = forms.partner.data;
  }

  if (forms.contacts) {
    result.forms.contacts = forms.contacts;
    result.record.contacts = map(forms.contacts, c => c.data);
  }

  if (forms.communication_record) {
    result.forms.communication_record = forms.communication_record;
    result.record.communication_record = forms.communication_record.data;
  }

  return result;
}

/**
 * Prepare local record object for sending to the api.
 */
function formsToApi(record) {
  return {
    data: {...record},
  };
}

/**
 * Submit data to create a communication record.
 */
export function doSubmit(validateOnly, onSuccess) {
  return async (dispatch, getState, {api}) => {
    const process = getState().process;
    const forms = formsToApi(process.record);
    try {
      const response = await api.submitContactRecord(forms, validateOnly);
      if (validateOnly) {
        dispatch(noteFormsAction(formsFromApi(response)));
      } else if (onSuccess) {
        onSuccess();
      }
    } catch (e) {
      if (e.data) {
        const apiErrors = e.data.api_errors;
        if (apiErrors) {
          dispatch(errorAction(apiErrors[0]));
        }
        if (e.data.forms) {
          dispatch(noteFormsAction(formsFromApi(e.data)));
        }
      } else {
        dispatch(errorAction(e.message));
      }
    }
  };
}
