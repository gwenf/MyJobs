// based on:
// http://stackoverflow.com/questions/24710503/how-do-i-post-urlencoded-form-data-with-http-in-angularjs
function ancientSerialize(obj) {
    var str = [];
    for(var p in obj)
    str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
    return str.join("&");
}

const hasFormData = !(window.FormData === undefined);

class Api {
    constructor(csrf) {
        this.csrf = csrf;
    }

    withCsrf(formData) {
        return {...formData, a: 1, csrfmiddlewaretoken: this.csrf};
    }

    checkStatus(response) {
        if (response.status == 200) {
            return response
        } else {
            var error = new Error(response.statusText)
            error.response = response
            throw error
        }
    }

    parseJSON(response) {
        return response.json();
    }

    objectToFormData(obj) {
        // No good way around this:
        if (hasFormData) {
            var formData = new FormData();
            Object.keys(obj).forEach(k => formData.append(k, obj[k]));
            return formData;
        } else {
            return ancientSerialize(obj);
        }

    }

    async postToReportingApi(url, data) {
        var formData = this.objectToFormData(this.withCsrf(data));
        var response = await fetch(url, {
            method: 'POST',
            body: formData,
            credentials: 'include',
            // No good way around this.
            headers: hasFormData ? undefined : {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });
        return this.parseJSON(this.checkStatus(response));
    }

    async getReportingTypes() {
        var promise = this.postToReportingApi("/reports/api/reporting_types", {});
        return (await promise)['reporting_type'];
    }

    async getReportTypes(reportingTypeId) {
        var formData = {
            reporting_type_id: reportingTypeId,
        };
        var promise = this.postToReportingApi("/reports/api/report_types", formData);
        return (await promise)['report_type'];
    }

    async getDataTypes(reportTypeId) {
        var formData = {
            report_type_id: reportTypeId,
        };
        var promise = this.postToReportingApi("/reports/api/data_types", formData);
        return (await promise)['data_type'];
    }

    async getPresentationTypes(reportTypeId, dataTypeId) {
        var formData = {
            report_type_id: reportTypeId,
            data_type_id: dataTypeId,
        };
        var promise = this.postToReportingApi("/reports/api/report_presentations", formData);
        return (await promise)['report_presentation'];
    }

    async runReport(reportPresentationId) {
        var formData = {
            rp_id: reportPresentationId,
        };
        return await this.postToReportingApi("/reports/api/run_report", formData);
    }
}

export {Api as default};
