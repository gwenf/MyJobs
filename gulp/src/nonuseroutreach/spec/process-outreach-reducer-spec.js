import reducer, {defaultState} from '../reducers/process-outreach-reducer';
import {
  resetProcessAction,
  determineProcessStateAction,
  choosePartnerAction,
  chooseContactAction,
  newPartnerAction,
  newContactAction,
  editFormAction,
  noteFormsAction,
  editPartnerAction,
  editContactAction,
  editCommunicationRecordAction,
  deletePartnerAction,
  deleteContactAction,
  deleteCommunicationRecordAction,
} from '../actions/process-outreach-actions';

describe('processEmailReducer', () => {
  describe('handling resetProcessAction', () => {
    const outreach = {
      summary: 'some title',
      body: 'some info',
    };
    const blankForms = [{1: 2}];
    const result = reducer({}, resetProcessAction(outreach, blankForms));

    it('should set the default state.', () => {
      expect(result.state).toEqual('SELECT_PARTNER');
    });

    it('should remember the given outreach', () => {
      expect(result.outreach).toDiffEqual(outreach);
    });

    it('should remember the given workflow blankForms', () => {
      expect(result.blankForms).toDiffEqual(blankForms);
    });
  });

  describe('handling choosePartnerAction', () => {
    const result = reducer({
      record: {partner: {}},
      forms: {},
    }, choosePartnerAction(4, 'acme'));

    it('should have the partner id', () => {
      expect(result.record.partner.pk).toEqual(4);
    });

    it('should have the partner name', () => {
      expect(result.record.partner.name).toEqual('acme');
    });
  });

  describe('handling chooseContactAction', () => {
    const state = {
      record: {
        partner: {
          pk: 4,
          name: 'acme',
        },
        contacts: [
          {pk: 99},
        ],
      },
      forms: {
        contacts: [],
      },
    };
    const result = reducer(state, chooseContactAction(3, 'bob'));

    it('should have the previous contacts', () => {
      expect(result.record.contacts[0]).toEqual(state.record.contacts[0]);
    });

    it('should have the contact id', () => {
      expect(result.record.contacts[1].pk).toEqual(3);
    });

    it('should have the contact name', () => {
      expect(result.record.contacts[1].name).toEqual('bob');
    });

    it('should retain the partner', () => {
      expect(result.record.partner).toEqual(state.record.partner);
    });

    it('places a null placeholder in the forms', () => {
      expect(result.forms.contacts[0]).toBe(null);
    });
  });

  describe('handling newPartnerAction', () => {
    const state = {
      record: {
        contacts: [{pk: {value: 3}}],
        partner: {pk: {value: 4}},
      },
      blankForms: {
        partner: {3: 4},
      },
    };
    const result = reducer(state, newPartnerAction('Partner Name Inc.'));

    it('should set the right state', () => {
      expect(result.state).toEqual('NEW_PARTNER');
    });

    it('should retain contacts', () => {
      expect(result.record.contacts).toEqual(state.record.contacts);
    });

    it('should have a blank partnerId', () => {
      expect(result.record.partner.pk).toEqual('');
    });

    it('should have a partner name', () => {
      expect(result.record.partner.name).toEqual('Partner Name Inc.');
    });

  });

  describe('handling newContactAction', () => {
    const state = {
      record: {
        contacts: [{pk: {value: 3}}],
        partner: {pk: {value: 4}},
      },
      forms: {
        contacts: [],
      },
      blankForms: {
        contacts: {3: 4},
      },
    };
    const result = reducer(state, newContactAction('Some Person'));

    it('set the right state', () => {
      expect(result.state).toEqual('NEW_CONTACT');
      expect(result.contactIndex).toEqual(1);
    });

    it('have a blank contactId', () => {
      expect(result.record.contacts[1].pk).toEqual('');
    });

    it('have a contact name', () => {
      expect(result.record.contacts[1].name).toEqual('Some Person');
    });

    it('keep the previous contacts', () => {
      expect(result.record.contacts[0]).toEqual(state.record.contacts[0]);
    });

    it('keep the partner', () => {
      expect(result.record.partner).toEqual(state.record.partner);
    });
  });

  describe('handling editFormAction', () => {

    describe('unindexed', () => {
      const action = editFormAction('partner', 'name', 'Bob');

      it('create and store the field', () => {
        const result = reducer({}, action);

        expect(result.record.partner.name).toEqual('Bob');
      });

      it('preserve other values', () => {
        const initialFormContents = {
          partner: {
            city: 'somewhere',
            suffix: 'jr',
          },
          other: {
            a: 'b',
          },
        };

        const action2 = editFormAction('partner', 'suffix', 'sr');
        let result = reducer({record: initialFormContents}, action);
        result = reducer(result, action2);

        expect(result.record).toDiffEqual({
          partner: {
            city: 'somewhere',
            name: 'Bob',
            suffix: 'sr',
          },
          other: {
            a: 'b',
          },
        });
      });
    });

    describe('indexed', () => {

      it('create and store the field', () => {
        const action = editFormAction('contacts', 'name', 'Bob', 0);
        const result = reducer({}, action);

        expect(result.record.contacts[0].name).toEqual('Bob');
      });

      it('should leave other indexed objects alone', () => {
        const initialFormContents = {
          contacts: [
            {
              city: 'somewhere',
              suffix: 'jr',
            },
            {
              city: 'elsewhere',
              suffix: 'jr',
            },
          ],
          other: {
            a: 'b',
          },
        };
        const action = editFormAction('contacts', 'city', 'elsewhere2', 1);
        const result = reducer({record: initialFormContents}, action);

        expect(result.record).toDiffEqual({
          contacts: [
            {
              city: 'somewhere',
              suffix: 'jr',
            },
            {
              city: 'elsewhere2',
              suffix: 'jr',
            },
          ],
          other: {
            a: 'b',
          },
        });
      });
    });
  });
});

describe('handling noteFormsAction', () => {
  const result = reducer({
    record: {3: 4},
    forms: {5: 6},
  }, noteFormsAction({record: {1: 2}, forms: {6: 7}}));

  it('should replace the whole record', () => {
    expect(result.record).toEqual({1: 2});
  });

  it('should replace the forms', () => {
    expect(result.forms).toEqual({6: 7});
  });
});

describe('handling editPartnerAction', () => {
  it('should switch state to new', () => {
    const result = reducer({}, editPartnerAction());
    expect(result.state).toEqual('NEW_PARTNER');
  });
});

describe('handling editContactAction', () => {
  describe('when there is no pk', () => {
    const result = reducer({}, editContactAction(3));

    it('should switch state', () => {
      expect(result.state).toEqual('NEW_CONTACT');
    });

    it('should set the contact index', () => {
      expect(result.contactIndex).toEqual(3);
    });
  });

  describe('when there is a pk', () => {
    const result = reducer({
      record: {
        contacts: [{pk: {value: 3}}],
      },
    }, editContactAction(0));

    it('should switch state', () => {
      expect(result.state).toEqual('CONTACT_APPEND');
    });

    it('should set the contact index', () => {
      expect(result.contactIndex).toEqual(0);
    });
  });
});

describe('handling editCommunicationRecordAction', () => {
  const result = reducer({}, editCommunicationRecordAction());

  it('should switch state', () => {
    expect(result.state).toEqual('NEW_COMMUNICATIONRECORD');
  });
});

describe('handling deleteContactAction', () => {
  const result = reducer({
    record: {
      contacts:[{pk: 3}, {pk: 4}],
    },
  }, deleteContactAction(0));

  it ('should remove contact by index', () => {
    expect(result.record.contacts).toEqual([{pk: 4}]);
  });
});

describe('handling deletePartnerAction', () => {
  const result = reducer({
    record: {
      partner: {pk: 1},
      contacts: [{pk: 1}, {pk: ''}],
    },
  }, deletePartnerAction(0));

  it ('should remove partner', () => {
    expect(result.record.partner).toEqual({});
  })

  it ('should remove any selected contacts that are linked to that partner',
    () => { expect(result.record.contacts).toEqual([{pk: ''}])
  });

});

describe('handling deleteCommunicationRecordAction', () => {
  const result = reducer({record: {communication_record: {stuff:'stuff'}}},
    deleteCommunicationRecordAction());

  it ('should delete communication record', () => {
    expect(result.record.communication_record).toEqual({});
  });
});

describe('handling determineProcessStateAction', () => {
  describe('without a partner' , () => {
    const result = reducer(
      {record: {}},
      determineProcessStateAction());

    it ('should direct to SELECT_PARTNER', () => {
      expect(result.state).toEqual('SELECT_PARTNER');
    })
  });
  describe('without any contacts but with a partner' , () => {
    const result = reducer(
      {record: {partner: {pk: 1}}},
      determineProcessStateAction());

    it ('should direct to SELECT_CONTACT', () => {
      expect(result.state).toEqual('SELECT_CONTACT');
    })
  });
  describe('without a comm rec but with a partner and contacts' , () => {
    const result = reducer({
      record: {partner: {pk: 1}, contacts: [{pk: 1}]},
      blankForms: {communication_record: {3: 4}},
    }, determineProcessStateAction());

    it ('should direct to NEW_COMMUNICATIONRECORD', () => {
      expect(result.state).toEqual('NEW_COMMUNICATIONRECORD');
    });

    it ('should set up a blank form', () => {
      expect(result.forms.communication_record).toEqual({3: 4});
    })
  });
});
