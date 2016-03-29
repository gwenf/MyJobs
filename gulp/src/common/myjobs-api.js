import param from 'jquery-param';

/**
 * Utility for making XHR calls from all our supported browsers.
 *
 * Also handles csrf and known response types.
 */
export class MyJobsApi {
  constructor(csrf) {
    this.csrf = csrf;
  }

  checkStatus(response) {
    if (response.status === 200) {
      return response;
    }

    const error = new Error(response.statusText);
    error.response = response;
    throw error;
  }

  parseJSON(response) {
    return response.json();
  }

  async get(url) {
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Accept': 'application/json',
      },
    });
    return this.parseJSON(this.checkStatus(response));
  }

  async ajaxWithFormData(method, url, data) {
    const formData = param(data);
    const response = await fetch(url, {
      method: method,
      body: formData,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': this.csrf,
        'Accept': 'application/json',
      },
    });
    return this.parseJSON(this.checkStatus(response));
  }

  async post(url, data) {
    return this.ajaxWithFormData('POST', url, data);
  }

  async delete(url, data) {
    return this.ajaxWithFormData('DELETE', url, data);
  }
}
