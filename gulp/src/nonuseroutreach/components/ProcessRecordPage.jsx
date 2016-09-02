import React, {PropTypes, Component} from 'react';
import {connect} from 'react-redux';
import FieldWrapper from 'common/ui/FieldWrapper';
import Card from './Card';
import Form from './Form';
import SearchDrop from './SearchDrop';
import {get} from 'lodash-compat/object';

import {
  contactNotesOnlyForm,
} from 'nonuseroutreach/forms';

import {
  resetSearchOrAddAction,
} from '../actions/search-or-add-actions';

import {
  determineProcessStateAction,
  choosePartnerAction,
  chooseContactAction,
  newPartnerAction,
  newContactAction,
  editFormAction,
  doSubmit,
} from '../actions/process-outreach-actions';

class ProcessRecordPage extends Component {
  resetSearches() {
    const {dispatch} = this.props;

    dispatch(resetSearchOrAddAction('PARTNER'));
    dispatch(resetSearchOrAddAction('CONTACT'));
  }

  handleChoosePartner(obj) {
    const {dispatch} = this.props;

    dispatch(choosePartnerAction(obj.value, obj.display));
    this.resetSearches();
    dispatch(determineProcessStateAction());
  }

  async handleChooseContact(obj, addPartner) {
    const {dispatch} = this.props;

    if (addPartner) {
      dispatch(choosePartnerAction(obj.partner.pk, obj.partner.name));
    }
    dispatch(chooseContactAction(obj.value, obj.display));
    this.resetSearches();
    dispatch(determineProcessStateAction());
  }

  async handleNewPartner(obj) {
    const {dispatch} = this.props;

    dispatch(newPartnerAction(obj.display));
  }

  async handleNewContact(obj) {
    const {dispatch} = this.props;

    dispatch(newContactAction(obj.display));
  }

  async handleSavePartner() {
    const {dispatch} = this.props;

    await dispatch(doSubmit(true));
    this.resetSearches();
    dispatch(determineProcessStateAction());
  }

  async handleSaveContact() {
    const {dispatch} = this.props;

    await dispatch(doSubmit(true));
    this.resetSearches();
    dispatch(determineProcessStateAction());
  }

  async handleSaveCommunicationRecord() {
    const {dispatch} = this.props;

    await dispatch(doSubmit(true));
    this.resetSearches();
    dispatch(determineProcessStateAction());
  }

  async handleSubmit() {
    const {dispatch, history} = this.props;

    await dispatch(doSubmit(false, () => history.pushState(null, '/records')));
    this.resetSearches();
  }

  renderCard(title, children) {
    return (
      <Card title={title}>
        {children}
      </Card>
    );
  }

  renderInitialSearch() {
    return this.renderCard('Partner Data', ([
      <div key="partner" className="product-card no-highlight clearfix">
        <FieldWrapper label="Partner Organization">
          <SearchDrop
            instance="PARTNER"
            onAdd={obj => this.handleNewPartner(obj)}
            onSelect={obj => this.handleChoosePartner(obj)}/>
        </FieldWrapper>
      </div>,
      <div key="contact" className="product-card no-highlight clearfix">
        <FieldWrapper label="Contact Search">
          <SearchDrop
            instance="CONTACT"
            onSelect={obj => this.handleChooseContact(obj, true)}/>
        </FieldWrapper>
      </div>,
    ]));
  }

  renderSelectContact() {
    const {partnerId} = this.props;

    return this.renderCard('Add Contact', ([
      <div key="contact" className="product-card no-highlight clearfix">
        <FieldWrapper label="Contact Search">
          <SearchDrop
            instance="CONTACT"
            extraParams={{partner_id: partnerId}}
            onSelect={obj => this.handleChooseContact(obj, false)}
            onAdd={obj => this.handleNewContact(obj)}
            />
        </FieldWrapper>
      </div>,
    ]));
  }

  renderNewCommunicationRecord() {
    const {
      dispatch,
      communicationRecordForm,
      communicationRecordFormContents,
    } = this.props;

    return (
      <Form
        form={communicationRecordForm}
        title="Communication Record"
        submitTitle="Add Record"
        formContents={communicationRecordFormContents}
        onEdit={(n, v) =>
          dispatch(editFormAction('communication_record', n, v))}
        onSubmit={() => this.handleSaveCommunicationRecord()}
        />
    );
  }

  renderNewPartner() {
    const {dispatch, partnerForm, partnerFormContents} = this.props;

    return (
      <Form
        form={partnerForm}
        title="Partner Data"
        submitTitle="Add Partner"
        formContents={partnerFormContents}
        onEdit={(n, v) => dispatch(editFormAction('partner', n, v))}
        onSubmit={() => this.handleSavePartner()}
        />
    );
  }

  renderNewContact() {
    const {
      dispatch,
      contactIndex,
      contactForms,
      contactFormsContents,
    } = this.props;

    const contactForm = contactForms[contactIndex];
    const contactFormContents = contactFormsContents[contactIndex] || {};

    return (
      <Form
        form={contactForm}
        title="Contact Details"
        submitTitle="Add Contact"
        formContents={contactFormContents}
        onEdit={(n, v) =>
          dispatch(editFormAction('contacts', n, v, contactIndex))}
        onSubmit={() => this.handleSaveContact()}
        />
    );
  }

  renderAppendContactNotes() {
    const {dispatch, contactIndex, contactFormsContents} = this.props;
    const contactFormContents = contactFormsContents[contactIndex] || {};

    return (
      <Form
        form={contactNotesOnlyForm}
        title="Contact Details"
        submitTitle="Add Contact"
        formContents={contactFormContents}
        onEdit={(n, v) =>
          dispatch(editFormAction('contacts', n, v, contactIndex))}
        onSubmit={() => this.handleSaveContact()}
        />
    );
  }

  renderSelectWorkflow() {
    const {
      dispatch,
      outreachRecordForm,
      outreachRecordFormContents,
    } = this.props;

    return (
      <Form
        form={outreachRecordForm}
        title="Form Ready for Submission"
        submitTitle="Submit"
        formContents={outreachRecordFormContents}
        onEdit={(n, v) =>
          dispatch(editFormAction('outreach_record', n, v, null))}
        onSubmit={() => this.handleSubmit()}
        />
    );
  }

  render() {
    const {processState} = this.props;

    let contents = '';
    let extraAddContact = '';

    if (processState === 'SELECT_PARTNER') {
      contents = this.renderInitialSearch();
    } else if (processState === 'SELECT_CONTACT') {
      contents = this.renderSelectContact();
    } else if (processState === 'NEW_COMMUNICATIONRECORD') {
      extraAddContact = this.renderSelectContact();
      contents = this.renderNewCommunicationRecord();
    } else if (processState === 'NEW_PARTNER') {
      contents = this.renderNewPartner();
    } else if (processState === 'NEW_CONTACT') {
      contents = this.renderNewContact();
    } else if (processState === 'CONTACT_APPEND') {
      contents = this.renderAppendContactNotes();
    } else if (processState === 'SELECT_WORKFLOW_STATE') {
      extraAddContact = this.renderSelectContact();
      contents = this.renderSelectWorkflow();
    }

    return (
      <div>
        <button className="nuo-button">
          <a href="/prm/view/nonuseroutreach/#/records">Back to record list</a>
        </button>
        {extraAddContact}
        {contents}
      </div>
    );
  }
}

ProcessRecordPage.propTypes = {
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  processState: PropTypes.string.isRequired,
  partnerId: PropTypes.any,
  partnerFormContents: PropTypes.object.isRequired,
  contactFormsContents: PropTypes.arrayOf(
    PropTypes.object.isRequired).isRequired,
  outreachRecordFormContents: PropTypes.object,
  contactIndex: PropTypes.number,
  communicationRecordFormContents: PropTypes.object.isRequired,
  partnerForm: PropTypes.object,
  contactForms: PropTypes.arrayOf(PropTypes.object),
  communicationRecordForm: PropTypes.object,
  outreachRecordForm: PropTypes.object,
};

export default connect(state => ({
  processState: state.process.state,
  partnerId: get(state.process, 'record.partner.pk'),
  contactIndex: state.process.contactIndex,
  partnerFormContents: state.process.record.partner,
  contactFormsContents: state.process.record.contacts,
  communicationRecordFormContents:
    state.process.record.communication_record,
  outreachRecordFormContents: state.process.record.outreach_record,
  partnerForm: state.process.forms.partner,
  contactForms: state.process.forms.contacts,
  communicationRecordForm: state.process.forms.communication_record,
  outreachRecordForm: state.process.forms.outreach_record,
}))(ProcessRecordPage);
