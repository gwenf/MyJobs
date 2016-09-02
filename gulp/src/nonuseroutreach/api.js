import {map} from 'lodash-compat/collection';

export default class Api {
  constructor(api) {
    this.api = api;
  }

  async getExistingInboxes() {
    return await this.api.get('/prm/api/nonuseroutreach/inbox/list');
  }

  async getExistingOutreachRecords() {
    return await this.api.get('/prm/api/nonuseroutreach/records/list');
  }

  async getWorkflowStates() {
    return await this.api.get('/prm/api/nonuseroutreach/workflowstate');
  }

  async createNewInbox(email) {
    const promise = this.api.post('/prm/api/nonuseroutreach/inbox/add', {
      email: email,
    });
    return (await promise);
  }

  async updateInbox(id, email) {
    const promise = this.api.post(
      '/prm/api/nonuseroutreach/inbox/update', {
        id: id,
        email: email,
      }
    );
    return (await promise);
  }

  async deleteInbox(id) {
    const promise = this.api.post(
      '/prm/api/nonuseroutreach/inbox/delete/', {'id': id}
    );
    return (await promise);
  }

  search(instance, searchString, extraParams) {
    return {
      PARTNER: (s, e) => this.searchPartner(s, e),
      CONTACT: (s, e) => this.searchContact(s, e),
    }[instance](searchString, extraParams);
  }

  async searchPartner(searchString) {
    const results =
      await this.api.post('/prm/api/partner', {'q': searchString});
    return map(results, r => ({value: r.id, display: r.name, count: r.contact_count}));
  }

  async searchContact(searchString, extraParams) {
    const results =
      await this.api.post('/prm/api/contact', {
        ...extraParams,
        'q': searchString,
      });
    return map(results, r => ({
      value: r.id,
      display: r.name,
      partner: r.partner,
    }));
  }

  async getOutreach(outreachId) {
    return await this.api.get(
      '/prm/api/nonuseroutreach/records/' + outreachId);
  }

  async getPartner(partnerId) {
    return await this.api.get('/prm/api/partner/' + partnerId);
  }

  async getForms() {
    return await this.api.get('/prm/api/nonuseroutreach/forms');
  }

  async submitContactRecord(request, validateOnly) {
    const uri = '/prm/api/nonuseroutreach/records/convert';
    const fullUri = validateOnly ? uri + '?validate_only=1' : uri;
    return await this.api.post(fullUri, {request: JSON.stringify(request)});
  }
}
