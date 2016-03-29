// Abstract the details of building urls and serializing requests for the
// reporting api.
//
// This uses the fetch api. Fetch works somewhat differently from jQuery.ajax.
// This module encapsulates all of that. Errors are translated to JS exceptions.


class Api {
  constructor(myJobsApi) {
    this.myJobsApi = myJobsApi;
  }

  async getFromReportingApi(url) {
    return this.myJobsApi.get(url);
  }

  async postToReportingApi(url, data) {
    return this.myJobsApi.post(url, data);
  }

  async listReports() {
    const response = await this.getFromReportingApi(
      '/reports/api/list_reports');
    return response.reports;
  }

  async getReportingTypes() {
    const promise = this.postToReportingApi('/reports/api/reporting_types', {});
    return (await promise).reporting_type;
  }

  async getReportTypes(reportingTypeId) {
    const formData = {
      reporting_type_id: reportingTypeId,
    };
    const promise = this.postToReportingApi('/reports/api/report_types', formData);
    return (await promise).report_type;
  }

  async getDataTypes(reportTypeId) {
    const formData = {
      report_type_id: reportTypeId,
    };
    const promise = this.postToReportingApi('/reports/api/data_types', formData);
    return (await promise).data_type;
  }

  async getPresentationTypes(reportTypeId, dataTypeId) {
    const formData = {
      report_type_id: reportTypeId,
      data_type_id: dataTypeId,
    };
    const promise = this.postToReportingApi('/reports/api/report_presentations', formData);
    return (await promise).report_presentation;
  }

  async getFilters(reportPresentationId) {
    const formData = {
      rp_id: reportPresentationId,
    };
    const promise = this.postToReportingApi(
          '/reports/api/filters',
          formData);
    return (await promise);
  }

  async getHelp(reportPresentationId, filter, field, partial) {
    const formData = {
      rp_id: reportPresentationId,
      filter: JSON.stringify(filter),
      field: field,
      partial: partial,
    };
    const promise = this.postToReportingApi(
          '/reports/api/help',
          formData);
    return (await promise);
  }

  async runReport(reportPresentationId, name, filter) {
    const formData = {
      name: name,
      filter: JSON.stringify(filter),
      rp_id: reportPresentationId,
    };
    return await this.postToReportingApi('/reports/api/run_report', formData);
  }
}

export {Api as default};
