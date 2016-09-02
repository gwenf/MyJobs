import processEmailReducer from '../reducers/process-outreach-reducer';
import errorReducer from '../../common/reducers/error-reducer';
import {keys} from 'lodash-compat';

import {
  doLoadEmail,
  resetProcessAction,
  convertOutreach,
  extractErrorObject,
  formatContact,
  flattenContact,
  formsFromApi,
  formsToApi,
} from '../actions/process-outreach-actions';

import {promiseTest} from '../../common/spec';

import createReduxStore from '../../common/create-redux-store';
import {combineReducers} from 'redux';

class FakeApi {
  getOutreach() {}
  getForms() {}
}

describe('convertOutreach', () => {
  const record = {
    date_added: "06-17-2016",
    from_email: "bob@example.com",
    email_body: "some text",
    outreach_email: "testemail@my.jobs",
    current_workflow_state: "Reviewed",
    subject: "Subject",
  };
  const result = convertOutreach(record);

  it('should change the keys of fields', () => {
    expect(result).toDiffEqual({
      dateAdded: "06-17-2016",
      outreachFrom: "bob@example.com",
      outreachBody: "some text",
      outreachInbox: "testemail@my.jobs",
      workflowState: "Reviewed",
      outreachSubject: "Subject",
    });
  });
});

describe('initial load', () => {
  let store;
  let api;

  beforeEach(() => {
    api = new FakeApi();
    store = createReduxStore(
      combineReducers({process: processEmailReducer, error: errorReducer}),
      {}, {api});
  });

  describe('after load', () => {
    const outreach = {
      from_email: "bob@example.com",
      email_body: "some text",
    };
    const blankForms = {6: 7};
    beforeEach(promiseTest(async () => {
      spyOn(api, 'getOutreach').and.returnValue(Promise.resolve(outreach));
      spyOn(api, 'getForms').and.returnValue(Promise.resolve({6: 7}));
      await store.dispatch(doLoadEmail(2));
    }));

    it('should have the outreach', () => {
      expect(store.getState().process.outreach).toDiffEqual(
        convertOutreach(outreach));
    });

    it('should have the outreachId', () => {
      expect(store.getState().process.record.outreach_record.pk).toEqual(2);
    });

    it('should have the blank forms', () => {
      expect(store.getState().process.blankForms).toEqual({6:7});
    });

    it('should be in the right state', () => {
      expect(store.getState().process.state).toEqual('SELECT_PARTNER');
    });
  });

  describe('after an error', () => {
    beforeEach(promiseTest(async () => {
      spyOn(api, 'getOutreach').and.throwError('some error');
      await store.dispatch(doLoadEmail(2));
    }));

    it('should remember the error', () => {
      expect(store.getState().error.lastMessage).toEqual('some error');
    });
  });
});
