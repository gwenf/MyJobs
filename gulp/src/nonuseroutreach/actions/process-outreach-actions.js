import {createAction} from 'redux-actions';
import {errorAction} from '../../common/actions/error-actions';
import {find} from 'lodash-compat/collection';

/**
 * We have a new search field or we are starting over.
 */
export const resetProcessAction = createAction('NUO_RESET_PROCESS',
  (outreachId, outreach) => ({outreachId, outreach}));

/**
 * Use chose a partner.
 *
 *  partnerId: database id of partner
 *  partner: partner data
 */
export const choosePartnerAction = createAction('NUO_CHOOSE_PARTNER',
    (partnerId, partner) => ({partnerId, partner}));

/**
 * Use chose a contact.
 *
 *  contactId: database id of contact
 *  contact: contact data
 */
export const chooseContactAction = createAction('NUO_CHOOSE_CONTACT',
    (contactId, contact) => ({contactId, contact}));

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
 * Form information arrived.
 *
 *  form: form data
 */
export const receiveFormAction = createAction('NUO_RECEIVE_FORM',
    (form) => ({form}));

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
  };
}

/**
 * Start the process by loading an outreach record.
 *
 * outreachId: id for the outreach to load.
 */
export function doLoadEmail(outreachId) {
  return async (dispatch, getState, {api}) => {
    try {
      const outreach = await api.getOutreach(outreachId);
      dispatch(resetProcessAction(outreachId, convertOutreach(outreach)));
    } catch (e) {
      dispatch(errorAction(e.message));
    }
  };
}

/**
 * Load a form definition from the api.
 *
 * formName: e.g. partner, contact, contactrecord, etc.
 * id: optional, id of item to prefill the form with.
 */
export function doLoadForm(formName, id) {
  return async (dispatch, _, {api}) => {
    try {
      const form = await api.getForm(formName, id);
      dispatch(receiveFormAction(form));
    } catch (e) {
      dispatch(errorAction(e.message));
    }
  };
}

/**
 * Submit data to create a communication record.
 */
export function doSubmit() {
  return async (dispatch, getState, {api}) => {
    const process = getState().process;
    const record = process.record;
    const workflowStates = await api.getWorkflowStates();
    const reviewed = find(workflowStates, s => s.name === 'Reviewed');
    const request = {
      outreachrecord: {
        pk: process.outreachId,
        current_workflow_state: reviewed.id,
      },
      partner: {pk: process.partnerId},
      contacts: [{pk: process.contactId}],
      contactrecord: {
        ...record.communicationrecord,
        date_time: '2016-1-1',
        contact_type: 'phone',
      },
    };
    await api.submitContactRecord(request);
    // TODO: do something with response.
  };
}