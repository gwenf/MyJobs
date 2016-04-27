class ReportingActions {
  constructor(api) {
    this.api = api;
  }

  doSetUpReport(intention, category, dataSet, reportDataId, filter, name) {
    return async (dispatch, getState) => {
      try {
        const reportInfo = getState();

        // Get menu and reportDataId for these menu choices.
        const choices = await this.api.getSetUpMenuChoices(intention,
            category, dataSet);
        const reportDataId = choices.report_data_id;

        // If we switched reportDataId's then push history.
        const currentReportDataId = getState().reportDataId;
        if (currentReportDataId !== reportDataId) {
          dispatch(push({
            pathName: '/set-up-report',
            query: {
              intention,
              category,
              dataSet,
              reportDataId,
              name
            },
          }));
        }

        // Note the new choices
        dispatch(updateSetUpMenuChoicesAction(choices))

        // If we didn't find a valid report id, we're done
        if (!reportDataId) {
          return;
        }

        // Get and note the column filters for this report.
        const fields = await this.api.getFilters(reportDataId);
        dispatch(updateFieldsAction(fields))

        // Pick a default name if none was provided.
        let name;
        if (currentName) {
          name = {name: currentName};
        } else {
          name = await this.api.getDefaultReportName(reportDataId);
        }
        dispatch(updateReportNameAction(name))
      } catch (exception) {
        if (exception.data) {
          const grouped = groupBy(exception.data, 'field');
          const fixed = mapValues(grouped, values => map(values, v => v.message));
          dispatch(apiErrorsAction(fixed));
        } else {
          dispatch(unhandledExceptionAction(exception);
        }
      }
    }
  }

  unhandledExceptionAction(exception) {
    return {
      type: 'UNHANDLED_EXCEPTION',
      exception,
  }

  apiErrorsAction(errors) {
    return {
      type: 'API_ERRORS',
      errors,
    }
  }

  updateSetUpMenuChoicesAction(choices) {
    return {
      type: 'UPDATE_SET_UP_MENU_CHOICES',
      choices,
    }
  }

  updateFieldsAction(fields) {
    return {
      type: 'UPDATE_FIELDS',
      fields,
    }
  }

  updateReportNameAction(name) {
    return {
      type: 'UPDATE_REPORT_NAME',
      name,
    }
  }
}
