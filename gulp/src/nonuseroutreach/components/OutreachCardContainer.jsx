import React, {PropTypes, Component} from 'react';
import {connect} from 'react-redux';
import OutreachCard from 'nonuseroutreach/components/OutreachCard';
import {isEmpty, map, filter, get, any} from 'lodash-compat';
import {
  determineProcessStateAction,
  editPartnerAction,
  deletePartnerAction,
  editContactAction,
  deleteContactAction,
  editCommunicationRecordAction,
  deleteCommunicationRecordAction,
} from '../actions/process-outreach-actions';


class OutreachCardContainer extends Component {
  handlePartnerNav() {
    const {dispatch, partner} = this.props;

    if (!get(partner, 'pk')) {
      dispatch(editPartnerAction());
    }
  }

  propsToCards() {
    const cardsReturn = [];
    for (const key in this.props) {
      if (this.props.hasOwnProperty(key) && !isEmpty(this.props[key])) {
        cardsReturn.push(this.switchCards(this.props[key], key));
      }
    }
    return cardsReturn;
  }

  switchCards(stateObject, type) {
    switch (type) {
    case 'contacts':
      return map(filter(stateObject, c => !isEmpty(c)),
        (contact, i) => this.renderContact(contact, i));
    case 'partner':
      return this.renderPartner(stateObject);
    case 'communicationRecord':
      return this.renderCommunicationRecord(stateObject);
    default:
      break;
    }
  }

  hasErrors(record) {
    return any(record, v => !isEmpty(v.errors));
  }

  renderContact(contact, index) {
    const {dispatch, contactsErrors} = this.props;

    return (
      <OutreachCard
        hasErrors={contactsErrors[index]}
        key={index}
        displayText={get(contact, 'name')}
        type="contact"
        onNav={() => dispatch(editContactAction(index))}
        onDel={() => {
          dispatch(deleteContactAction(index));
          dispatch(determineProcessStateAction());
        }} />
    );
  }

  renderPartner(partner) {
    const {dispatch, partnerErrors} = this.props;

    return (
      <OutreachCard
        hasErrors={partnerErrors}
        key="partner"
        type="partner"
        displayText={get(partner, 'name')}
        onNav={() => this.handlePartnerNav()}
        onDel={() => {
          dispatch(deletePartnerAction());
          dispatch(determineProcessStateAction());
        }} />
    );
  }

  renderCommunicationRecord() {
    const {
      dispatch,
      communicationRecord,
      communicationRecordErrors,
    } = this.props;

    return (
      <OutreachCard
        hasErrors={communicationRecordErrors}
        displayText={get(communicationRecord, 'contact_type', 'unknown')}
        type="communicationrecord"
        onNav={() =>
          dispatch(editCommunicationRecordAction())}
        onDel={() => dispatch(deleteCommunicationRecordAction())}
        key="commrec" />
    );
  }

  render() {
    const outreachCards = this.propsToCards();
    return (
      <div>
        {outreachCards}
      </div>
    );
  }
}

OutreachCardContainer.defaultProps = {
  contacts: [],
};

OutreachCardContainer.propTypes = {
  dispatch: PropTypes.func.isRequired,
  partner: PropTypes.object,
  partnerErrors: PropTypes.bool.isRequired,
  contacts: PropTypes.array,
  contactsErrors: PropTypes.arrayOf(PropTypes.bool.isRequired).isRequired,
  communicationRecord: PropTypes.object,
  communicationRecordErrors: PropTypes.bool.isRequired,
};

function getErrorsForForm(forms, key) {
  return !isEmpty(get(forms, [key, 'errors']));
}

function getErrorsForForms(forms, key) {
  return map(get(forms, key), f => !isEmpty(get(f, 'errors')));
}

export default connect(state => ({
  partner: state.process.record.partner,
  partnerErrors: getErrorsForForm(state.process.forms, 'partner'),
  contacts: state.process.record.contacts,
  contactsErrors: getErrorsForForms(state.process.forms, 'contacts'),
  communicationRecord: state.process.record.communication_record,
  communicationRecordErrors: getErrorsForForm(
    state.process.forms,
    'communication_record'),
}))(OutreachCardContainer);
