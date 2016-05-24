window.onpopstate = function(event) {
  var state = event.state,
      $sidebar = $(".sidebar"),
      historyNew,
      historyClone,
      report;

  if (state.page && state.page === 'overview') {
    navigation = false;
    renderOverview();
  } else if (state.page && state.page === 'new') {
    historyNew = function() {
      var types = state.types,
          form,
          report,
          rs;

      if (types.length > 1) {
        rs = types.map(function(type) {
          return createReport(type);
        });
        form = new Form(rs);
      } else {
        report = createReport(types[0]);
      }


      $("#container").addClass("rpt-container");
      if (form) {
        form.renderReports(".rpt-container");
      } else {
        report.renderFields(".rpt-container", report.fields, true);
        report.unbindEvents().bindEvents();
      }
      renderNavigation();
    };

    navigation = true;
    $sidebar.find('h2:contains("Past Reports")').length > 0 ? historyNew() : renderOverview(historyNew);
  } else if (state.page && state.page === 'view-report') {
    var callback = function() {
          renderNavigation(true);
        },
        render = {
          contact: function() {return renderViewContact(state.reportId, state.reportName);},
          partner: function() {return renderViewPartner(state.reportId, state.reportName);},
          contactrecord: function() {return renderGraphs(state.reportId, state.reportName, callback);}
        };
    navigation = true;
    render[state.model]();
  } else if (state.page && state.page === 'report-archive') {
    navigation = true;
    renderArchive(renderNavigation);
  } else if (state.page && state.page === 'report-download') {
    renderDownload(state.report);
  } else if (state.page && state.page === 'clone') {
    historyClone = function() {
      report = createReport(state.type);
      report.createCloneReport(state.inputs);
      $("#container").addClass("rpt-container");
      report.renderFields(".rpt-container", report.fields, true);
      report.unbindEvents().bindEvents();
      renderNavigation();
    };

    navigation = true;
    $sidebar.find('h2:contains("Past Reports")').length > 0 ? historyClone() : renderOverview(historyClone);
  }
};


// Determines if IE10+ is being used.
var modernBrowser = !(isIE() && isIE() < 10);

// Determines if a navigation bar is needed.
var navigation = false;

// Gives the ability for AJAX to send Arrays.
$.ajaxSettings.traditional = true;

function Form(reports) {
  this.reports = reports;
}

Form.prototype = {
  renderReports: function(renderAt) {
    this.reports.forEach(function(report, index, array) {
      report.renderFields(renderAt, report.fields, index === 0, index + 1 === array.length);
    });
  }
};


// Handles storing data, rendering fields, and submitting report. See prototype functions
function Report(type, fields) {
  this.data = {filters: {}};
  this.fields = fields;
  this.type = type;

  var report = this;

  this.fields.forEach(function(field) {
    field.report = report;
  });
}

Report.prototype = {
  typeVerbose: function() {
    var verbose = {
      'contactrecord': "Communication Records",
      'partner': "Partner",
      'contact': "Contact"
    };
    return verbose[this.type] + " Report";
  },
  renderFields: function(renderAt, fields, clear, btn) {
    var $renderAt = $(renderAt),
        c = typeof clear !== "undefined" ? clear : true,
        b = typeof btn !== "undefined" ? btn : true,
        field,
        i;

    // Clear what is currently in the container.
    if (c) {
      $renderAt.html("");
    }

    $renderAt.append('<h2 class="report-heading">' + this.typeVerbose() + '</h2>');

    // for field in fields render.
    for (i = 0; i < fields.length; i++) {
      field = fields[i];
      if (!field.dom().length) {
        $renderAt.append(field.render());

        if (field instanceof FilteredList && !field.filterAfter().length) {
          field.filter();
        }
        if (typeof field.bindEvents !== "undefined") {
          field.bindEvents();
        }
      }
    }

    if (b) {
      $renderAt.append('<div class="show-modal-holder">' +
      '<a id="show-modal" class="btn primary">Generate Report</a>' +
      '</div>');
    }

    return this;
  },
  findField: function(fieldID) {
    return this.fields.filter(function (field) {
      return (field.id === fieldID ? field : undefined);
    })[0];
  },
  createCloneReport: function(json) {
    // We can't simply iterate over the json keys because they are in the
    // nested object format, and the only reference to fields we have are their
    // IDs and key values. Thus, we iterate over each key and see if we can
    // grab them from the json by key.
    var formatDate = function(string) {
          var date = string.split(" ")[0].split("-");
          return [date[1], date[2], date[0]].join("/");
        };

    this.fields.forEach(function(field) {
      // I needed to be able to set defaultVal to undefined on each iteration,
      // but didn't want to shadow the value undefined. Null was insufficient
      // as then I'd have to later check for null and undefined.
      var defaultVal = void 0;
      // DateField is special since it contains two values, so we need to check
      // for  both values and combine them into a single default value.
      if (field instanceof DateField) {
        var start_date = steelToe(json).get(field.key.start_date),
            end_date = steelToe(json).get(field.key.end_date);

        if (typeof start_date !== 'undefined' && typeof end_date !== 'undefined') {
          defaultVal = {
            start_date: formatDate(start_date),
            end_date: formatDate(end_date)
          };
        }
      } else {
        defaultVal = steelToe(json).get(field.key);

        // We store list values as an integer, but expect them as strings for
        // the form instances, which is why we conver them here if they exist
        if (field instanceof FilteredList && typeof defaultVal !== 'undefined') {
          defaultVal = defaultVal.map(function(item) {
            return item.toString();
          });
        }
      }

      if (typeof defaultVal !== 'undefined') {
        field.defaultVal = defaultVal;
      }
    });
  },
  bindEvents: function() {
    var report = this,
        container = $("#main-container");

    container.on("click", "#show-modal:not('.disabled')", function () {
      var modal = $("#report-modal"),
        body = modal.children(".modal-body"),
        footer = modal.children(".modal-footer"),
        saved;

      saved = report.save();

      if (saved) {
        body.html(report.readableData());
        modal.modal("show");
      }
    });

    $("body").on("click.submit", "#gen-report:not('disabled')", function () {
      var csrf = readCookie("csrftoken"),
          data = {"csrfmiddlewaretoken": csrf},
          url = location.protocol + "//" + location.host + "/reports/view/mypartners/" + report.type,
          newList = [];
      if (report.data) {
        $.extend(data, report.data);
        data.filters = JSON.stringify(data.filters);
      }
      if (data.contact) {
        for (var i = 0; i < data.contact.length; i++) {
          var value = data.contact[i],
              name = $("#contact input[data-pk='" + value + "']").parent().text().split('(')[0].trim();
          newList.push(name);
        }
        delete data.contact;
        data.contact__name = newList;
      }

      $.ajax({
        type: 'POST',
        url: url,
        data: $.param(data, true),
        success: function (data) {
          window.location = location.protocol + '//' + location.host + location.pathname;
        }
      });
    });

    return this;
  },
  unbindEvents: function() {
    $("body").off(".submit");
    $("#main-container").off("click");

    return this;
  },
  hasErrors: function() {
    return this.fields.some(function (field) {
      return field.errors.length;
    });
  },
  save: function() {
    var report = this,
        errors;

    this.fields.forEach(function (field) {
      field.validate(false);
    });

    errors = this.fields.filter(function (field) {
      return field.errors.length > 0;
    });

    if (errors.length) {
      errors.forEach(function (field) {
        field.showErrors();
      });
      return false;
    } else {
      this.fields.forEach(function (field) {
        $.extend(true, field.isFilter ? report.data.filters : report.data, field.onSave());
      });
    }

    return true;
  },
  readableData: function(d) {
    return this.fields.map(function(element) {
      return element.readableData();
    }).join("");
  }
};


function defaults(options, defaultOptions) {
  if (typeof options === 'object') {
    options = $.extend(defaultOptions, options);
  } else {
    options = defaultOptions;
  }

  return options;
}


function Field(options) {
  $.extend(this, defaults(options, {
    label: "Default Label",
    id: "DefaultID",
    required: false,
    defaultVal: '',
    helpText: '',
    errors: [],
    isFilter: true,
    autofocus: ''
  }));

  this.key = this.key || options.id;
}

Field.prototype = {
  bind: function(event, selector, callback) {
    if (arguments.length === 2) {
      callback = selector;
      selector = undefined;
    }

    $(this.dom()).on(event, selector, function (e) {
      callback(e);
    });

    return this;
  },
  currentVal: function() {
    return this.dom().val();
  },
  dom: function() {
    return $("#" + this.id);
  },
  onSave: function(key) {
    var data = {},
        value = this.currentVal();

    if(value) {
      steelToe(data).set(key || this.key, value);
    }

    return data;
  },
  removeErrors: function() {
    var $field = $(this.dom()),
        $showModal = $("#show-modal");

    if ($field.parent("div.required").length) {
      $field.prev(".show-errors").remove();
      $field.unwrap();
    }

    if (!this.report.hasErrors()) {
      $showModal.removeClass("disabled");
    }

    return this;
  },
  renderLabel: function() {
    return '<label class="big-blu" for="' + this.id + '">' + this.label + (this.required ? '<span style="color: #990000;">*</span>' : '') + '</label>';
  },
  showErrors: function() {
    var $field = $(this.dom()),
        $showModal = $("#show-modal");

    if (this.errors.length) {
      if (!$field.parent("div.required").length) {
        $field.wrap('<div class="required"></div>');
      }

      if (!$field.prev(".show-errors").length) {
        $field.before('<div class="show-errors">' + this.errors.join(', ') + '</div>');
      } else {
        $field.prev().html(this.errors.join(','));
      }
      $showModal.addClass("disabled");
    }
  },
  unbind: function(event) {
    $(this.dom()).off(event);

    return this;
  },
  validate: function() {
    var err = this.label + " is required",
        index = this.errors.indexOf(err);

    if (this.required && this.currentVal().trim() === "") {
      if (index === -1) {
        this.errors.push(err);
        this.showErrors();
      }
    } else {
      if (index !== -1) {
        this.errors.splice(index, 1);
        this.removeErrors();
      }
    }

    return this;
  },
  readableData: function(key, value) {
    key = (key || this.id).replace(/_/g, " ");
    value = value || this.currentVal();
    var html = '<div>',
        items = [],
        i;

    if (value && value.length) {
      html += '<label>' + key.capitalize() + ':</label>';
    }

    if (typeof value === "object" && value !== null && value.length) {
      if (key === "partner" || key === "contact") {
        for (i = 0; i < value.length; i++) {
          items.push($('#' + key + ' input[data-pk=' + value[i] + ']').parent().text());
        }
      } else {
        for (i = 0; i < value. length; i++) {
          items.push(value[i]);
        }
      }
      html += '<ul class="short-list"><li>' + items.join('</li><li>') + '</li></ul>';
    } else {
      html += value;
    }
    html += '</div>';

    return html;
  }
};


function TextField(options) {
  Field.call(this, options);
}

// TextField prototype inherits Field's prototype then overwrites
// or adds methods if different from default functionality.
TextField.prototype = $.extend(Object.create(Field.prototype), {
  bindEvents: function() {
    var textField = this,
        $field = $(textField.dom()),
      trim = function () {
        var value = $field.val().trim();
        $field.val(value);
      };

    this.bind("change.validate", function (e) {
      textField.validate();
    });

    this.bind("change.trim", trim);
  },
  render: function() {
    var label = this.renderLabel(),
        field = '<input id="' + this.id + '" value="' + this.defaultVal +
          '" type="text" placeholder="' + this.label + (this.autofocus?
          '" autofocus="autofocus" />' : '" />'),
        helpText = '<div class="help-text">' + this.helpText + '</div>';
    return label + field + (this.helpText ? helpText : '');
  }
});


function CheckBox(options) {
  options.checked = typeof options.checked === 'undefined' ? true : options.checked;
  options.name = options.name;
  options.id = options.name + '_' + options.defaultVal;

  Field.call(this, options);
}

CheckBox.prototype = $.extend(Object.create(Field.prototype), {
  render:  function(createLabel) {
    createLabel = typeof createLabel === 'undefined' ? true : createLabel;

    var label = this.renderLabel(),
      field = '<label class="field"><input id="' + this.id + '" name="' + this.name +
        '" type="checkbox" value="' + this.defaultVal +
        (this.checked ? '" checked />' : '" />') + this.label + '</label>',
      helpText = '<div class="help-text">' + this.helpText + '</div>';

    return (createLabel ? label : '') + field + (this.helpText ? helpText : '');
  }
});

function CheckList(options) {
  this.choices = options.choices;

  Field.call(this, options);
}

CheckList.prototype = $.extend(Object.create(Field.prototype), {
  bindEvents: function() {
    var checklist = this;

    this.bind("change", "[value='all']", function (e) {
      var $all = $(e.currentTarget),
          $choices = $(checklist.dom()).find(".field input");

      $choices.prop("checked", $all.is(":checked"));
      $($choices[$choices.length - 1]).change();
    });

    this.bind("change", ".field input", function () {
      var choices = $(checklist.dom()).find(".field input").toArray(),
          $all = $(checklist.dom()).find("[value='all']"),
          checked;

      checked = choices.every(function (c) {
        return $(c).is(":checked");
      });
      $all.prop("checked", checked);

      checklist.choices.forEach(function (element) {
        element.checked = $(element.dom()).is(":checked");
      });

      checklist.validate();
    });
  },
  currentVal: function() {
    var values = $.map(this.choices, function (c) {
      if (c.checked) {
        return c.currentVal();
      }
    });

    return values.length ? values : ["0"];
  },
  render: function() {
    var label = this.renderLabel(),
        html = $.map(this.choices, function (choice) {
          return choice.render(false);
        }).join("  ");

    return label + '<div class="checklist" id="' + this.id + '">' +
      '<label style="display: inline;"><input value="all" type="checkbox" checked/ >All</label>  ' + html +
      '</div>';
  },
  validate: function() {
    var err = this.label + " is required",
        index = this.errors.indexOf(err),
        value = this.currentVal();

    if (this.required && value.indexOf("0") === 0 && value.length === 1) {
      if (index === -1) {
        this.errors.push(err);
        this.showErrors();
      }
    } else {
      if (index !== -1) {
        this.errors.splice(index, 1);
        this.removeErrors();
      }
    }

    return this;
  }
});


function DateField(options) {
  Field.call(this, options);
}

DateField.prototype = $.extend(Object.create(Field.prototype), {
  bindEvents: function() {
    var dateField = this,
        datePicker = function (e) {
          var $targeted = $(e.currentTarget);
          $targeted.pickadate({
            format: "mm/dd/yyyy",
            selectYears: true,
            selectMonths: true,
            min: [2014, 0, 1], // PRM started in 2014/1/1
            max: true,
            today: false,
            clear: false,
            close: false,
            onOpen: function () {
              if (this.get("id") === "start-date") {
                var end_date = $("#end-date").val();
                this.set("max", end_date ? new Date(end_date) : true);
              } else if (this.get("id") === "end-date") {
                var start_date = $("#start-date").val();
                this.set("min", start_date ? new Date(start_date) : [2014, 0, 1]);
              }
            }
          });
        };

    this.bind("focus.datepicker", ".datepicker", datePicker);
    this.bind("change.validate", ".datepicker", function (e) {
      dateField.validate();
    });
  },
  currentVal: function(id) {
    return $(this.dom()).find("#" + id).val();
  },
  onSave: function(key) {
    var data = {};
    steelToe(data).set((key || this.key).start_date, reportNameDateFormat(new Date(this.currentVal("start-date"))));
    steelToe(data).set((key || this.key).end_date, reportNameDateFormat(new Date(this.currentVal("end-date")), true));
    return data;
  },
  render: function() {
    var label = this.renderLabel(),
        dateWidget = $('<div id="' + this.id + '" class="filter-option"><div class="date-picker"></div></div>'),
        datePicker = $(dateWidget).find(".date-picker"),
        to = '<span id="activity-to-" class="datepicker">to</span>',
        start = '<input id="start-date" class="datepicker picker-left" type="text" value="' + (this.defaultVal ? this.defaultVal.start_date : "") + '" placeholder="Start Date" />',
        end = '<input id="end-date" class="datepicker picker-right" type="text" value="' + (this.defaultVal ? this.defaultVal.end_date : "") + '" placeholder="End Date" />';

    datePicker.append(start).append(to).append(end);
    dateWidget.append(datePicker);
    return label + dateWidget.prop("outerHTML");
  },
  validate: function() {
    var dateField = this,
        $dom = $(this.dom()),
        $fields = $dom.find("input.datepicker"), // Both start and end inputs.
        label,
        err;

    $.each($fields, function (index, field) {
      label = $(field).attr('placeholder');
      err = label + " is required";
      index = dateField.errors.indexOf(err);
      if ($(field).val() === "") {
        if (index === -1) {
          dateField.errors.push(label + " is required");
          dateField.showErrors();
        }
      } else {
        if (index !== -1) {
          dateField.errors.splice(index, 1);
          dateField.removeErrors();
        }
      }
    });

    return this;
  },
  readableData: function() {
    var start_date = Field.prototype.readableData('start_date', this.currentVal('start-date')),
        end_date = Field.prototype.readableData('end_date', this.currentVal('end-date'));

    return start_date + end_date;
  }
});


function StateField(options) {
  Field.call(this, options);
}

StateField.prototype = $.extend(Object.create(Field.prototype), {
  bindEvents: function() {
    var stateField = this;

    $(document).on("change.validate", "#" + stateField.id, function () {
      stateField.validate();
    });
  },
  render: function() {
    var label = this.renderLabel(),
        $select = $('<select id="' + this.id + '"></select>'),
        options = ['<option value="">Select a State</option>'],
        st;

    // create options
    for (st in states) {
      if (states.hasOwnProperty(st)) {
        options.push('<option value="' + st + '" ' + (this.defaultVal === st ? "selected" : "") + '>' + states[st] + '</option>');
      }
    }

    $select.append(options.join(''));
    return label + $select.prop("outerHTML");
  }
});


function TagField(options) {
  this.value = [];
  TextField.call(this, options);
}

TagField.prototype = $.extend(Object.create(TextField.prototype), {
  bindEvents: function() {
    var tagField = this,
      $dom = $(this.dom());

    $dom.autocomplete({
      focus: function () {
        // Prevent value inserted on focus.
        return false;
      },
      select: function (event, ui) {
        // Split string by "," then trim whitespace on either side of all inputs.
        var inputs = this.value.split(",").map(function (i) {
          return i.trim();
        });

        // Remove last element of inputs. Typically is an unfinished string.
        inputs.pop();
        // Add selected item from autocomplete
        inputs.push(ui.item.value);
        // Add placeholder for join to create an extra ", " for UX goodness.
        inputs.push("");
        // Combine everything in inputs with ", ".
        this.value = inputs.join(", ");

        // If there are any inputs already in the field make sure default functionality doesn't run.
        if (inputs.length) {
          return false;
        }
      },
      source: function (request, response) {
        var inputs = request.term.split(",").map(function (i) {
            return i.trim();
          }),
        // Last element is always going to be what is being searched for.
          keyword = inputs.pop(),
        // Initialize list of suggested tag names.
          suggestions,
          tagData = {
            filters: {
              name: {
                icontains: keyword,
              }
            },
            values: ["name"],
            order_by: "name",
            csrfmiddlewaretoken: readCookie("csrftoken"),
          };

        tagData.filters[tagField.report.type] = {
          isnull: false
        };

        tagData.filters = JSON.stringify(tagData.filters);

        $.ajax({
          type: "POST",
          url: "/reports/ajax/mypartners/tag",
          //TODO: New backend changes will fix this monstrocity
          data: tagData,
          success: function (data) {
            suggestions = data.filter(function (d) {
              // Don't suggest things that are already selected.
              if (inputs.indexOf(d.name) === -1) {
                return d;
              }
            }).map(function (d) {
              // Only care about name string.
              return d.name;
            });

            response(suggestions);
          }
        });
      }
    });

    $dom.on("autocompleteopen", function () {
      $dom.data("isOpen", true);
    });

    $dom.on("autocompleteclose", function () {
      $dom.data("isOpen", false);
      tagField.value = $dom.val();
      tagField.validate();
    });

    $dom.on("change", function () {
      if (!$dom.data("isOpen")) {
        tagField.value = $dom.val();
        tagField.validate();
      }
    });
  },
  currentVal: function() {
    // Split on commas. Trim each element in array. Remove any elements that were blank strings.
    return this.dom().val().split(",").map(function (t) {
      return t.trim();
    }).filter(function (t) {
      if (!!t) {
        return t;
      }
    });
  },
  onSave: function(key) {
    var data = {};

    if (this.value.length) {
      steelToe(data).set(key || this.key, this.currentVal());
    }

    return data;
  }
});


function FilteredList(options) {
  $.extend(this, defaults(options, {
    dependencies: null,
    order_by: null,
    values: null
  }));

  // used internally, shouldn't be changed by consumers of the API
  this.active = 0;
  this.hasRun = false;

  Field.call(this, options);
}

FilteredList.prototype = $.extend(Object.create(Field.prototype), {
  filterAfter: function() {
    var filteredList = this,
        report = this.report;

    return Object.keys(filteredList.dependencies).map(function(id) {
      return report.findField(id);
    }).filter(function(field) {
      return field instanceof FilteredList;
    });
  },
  currentVal: function() {
    ids = $(this.dom()).find(":checked").toArray().map(function(element) {
      return $(element).data('pk');
    });

    return ids;
  },
  bindEvents: function() {
    var filteredList = this,
        $header = $('#' + filteredList.id + '-header'),
        $recordCount = $header.find(".record-count"),
        $all = $header.find("input"),
        $dom = $(this.dom());

    if (filteredList.dependencies) {
      dependencies = Object.keys(filteredList.dependencies).map(function(e) {
        return "#" + e;
      }).join(", ");

      $(dependencies).on("change autocompleteclose", function(e) {
        filteredList.filter();
      });

      $dom.on("filtered", function (e, field) {
        if (Object.keys(filteredList.dependencies).indexOf(field) !== -1) {
          filteredList.filter();
        }
      });
    }

    $header.on("click", function () {
      var $this = $(this),
          $icon = $this.children("i:first");

      if ($icon.hasClass("fa-plus-square-o")) {
        $icon.removeClass("fa-plus-square-o").addClass("fa-minus-square-o");
      } else {
        $icon.removeClass("fa-minus-square-o").addClass("fa-plus-square-o");
      }

      $this.next().stop(true, true).slideToggle();
    });

    $header.on("change", "input", function () {
      var $choices = $(filteredList.dom()).find("input");

      $choices.prop("checked", $(this).is(":checked"));
      $($choices[$choices.length - 1]).change();

    });

    $dom.bind("change", "input", function () {
      var choices = $(filteredList.dom()).find("input").toArray(),
          checked,
          value;

      checked = choices.every(function (c) {
        return $(c).is(":checked");
      });
      $all.prop("checked", checked);
      value = filteredList.currentVal();
      $recordCount.text(value.length === 1 && value.indexOf("0") === 0 ? 0 : value.length);
    });

    $all.on("change", function (e) {
      filteredList.validate();
    });

    $dom.bind("change.validate", "input", function (e) {
      filteredList.validate();
    });
  },
  filter: function() {
    var filteredList = this,
        report = this.report,
        dependencies = this.dependencies,
        id,
        $recordCount,
        $listBody,
        $input,
        filterData = {
          filters:{},
          values: filteredList.values,
          order_by: filteredList.order_by,
          csrfmiddlewaretoken: readCookie("csrftoken")
        };

    for (id in dependencies) {
      if (dependencies.hasOwnProperty(id)) {
        $.extend(true, filterData.filters, report.findField(id).onSave(dependencies[id]));
      }
    }

    filterData.filters = JSON.stringify(filterData.filters);

    return $.ajax({
      type: "POST",
      url: "/reports/ajax/mypartners/" + this.id,
      data: filterData,
      global: false,
      beforeSend: function () {
        $('#' + filteredList.id + '-header > span').hide();
        if (!$('#' + filteredList.id + '-header > .fa-spinner').length) {
          $('#' + filteredList.id + '-header').append('<i style="margin-left: 5px;" class="fa fa-spinner fa-pulse"></i>');
        }

        filteredList.active++;
      },
    }).done(function(data) {
      $recordCount = $('#' + filteredList.id + '-header .record-count');
      $listBody = $('.list-body#' + filteredList.id);
      $listBody.html("").parent(".required").children().unwrap().prev('.show-errors').remove();
      $listBody.append('<ul><li>' + data.map(function (element) {
        $input = $('<input type="checkbox" data-pk="' + element.pk + '" ' + (function () {
          if (filteredList.defaultVal && !filteredList.hasRun) {
            return filteredList.defaultVal.indexOf(element.pk.toString()) >= 0 ? "checked" : "";
          }
          return "checked";
        })() + '/>');
        return '<label>' + $input.prop("outerHTML") + ' ' + element.name +
          (filteredList.id === 'contact' && element.email ? ' <span class="small">(' + element.email + ')</span>' : '') + '</label>';
      }).join("</li><li>") + '</li></ul>');

      var value = filteredList.currentVal();
      if (!filteredList.hasRun) {
        $('#' + filteredList.id + '-header input').prop("checked", $(filteredList.dom()).find("input").toArray().every(function (c) {
          return $(c).is(":checked");
        }));
      } else {
        $('#' + filteredList.id + '-header input').prop("checked", true);
      }
      $recordCount.text(value.length === 1 && value.indexOf("0") === 0 ? 0 : value.length);

      filteredList.active--;
      if (!filteredList.active) {
        $('#' + filteredList.id + '-header > .fa-spinner').remove();
        $('#' + filteredList.id + '-header > span').show();
        $.event.trigger("filtered", [filteredList.id]);
      }
      filteredList.hasRun = true;
    });
  },
  removeErrors: function() {
    var $header = $('#' + this.id + '-header'),
        $showModal = $('#show-modal');

    if ($header.parent(".required").length) {
      $header.prev(".show-errors").remove();
      $header.unwrap();
    }

    if (!this.report.hasErrors()) {
      $showModal.removeClass("disabled");
    }

    return this;
  },
  render: function() {
    var label = this.renderLabel(),
        body = '<div id="' + this.id + '" style="display: none;" class="list-body"></div>';

    return label + body;
  },
  renderLabel: function() {
    return '<div id="' + this.id + '-header" class="list-header">' +
      '<i class="fa fa-plus-square-o"></i>' +
      '<input id="' + this.id + '-all-checkbox" type="checkbox" ' + (this.defaultVal ? "" : "checked") + ' />' +
      ' All ' + this.label + (this.required ? '<star style="color: #990000">*</star>' : '') +
      ' <span>(<span class="record-count">0</span> ' + this.label + ' Selected)</span>' +
      '</div>';
  },
  showErrors: function() {
    var $header = $('#' + this.id + '-header'),
        $fuse = $('#' + this.id + '-header, #' + this.id),
        $showModal = $('#show-modal');

    if (this.errors.length) {
      if (!$fuse.parent(".required").length) {
        $fuse.wrapAll('<div class="required"></div>');
      }

      if (!$header.prev(".show-errors").length) {
        $header.before('<div class="show-errors">' + this.errors.join(', ') + '</div>');
      } else {
        $header.prev().html(this.errors.join(','));
      }
      $showModal.addClass("disabled");
    }

    return this;
  },
  validate: function() {
    var err = this.label + " is required",
      index = this.errors.indexOf(err),
      value = this.currentVal();

    if (this.required && value.indexOf("0") === 0 && value.length === 1) {
      if (index === -1) {
        this.errors.push(err);
        this.showErrors();
      }
    } else {
      if (index !== -1) {
        this.errors.splice(index, 1);
        this.removeErrors();
      }
    }

    return this;
  }
});


// Capitalize first letter of a string.
String.prototype.capitalize = function() {
  return this.charAt(0).toUpperCase() + this.slice(1);
};

var yesterday = (function(d){d.setDate(d.getDate() - 1); return d; })(new Date());


$(document).ready(function() {
  var $subpage = $(".subpage");

  $("#choices input[name='report']:checked").prop("checked", false);

  if (modernBrowser) {
    history.replaceState({'page': 'overview'}, "Report Overview");
  }

  $subpage.on("click", "#start-report:not(.disabled)", function(e) {
    e.preventDefault();
    var choices = $("#choices input[name='report']:checked"),
        types = [],
        i = 0,
        form,
        rs,
        report;

    // fill types with choices that are checked, see selector.
    for (i; i < choices.length; i++) {
      types.push(choices[i].value.toLowerCase());
    }

    if (types.length > 1) {
      rs = types.map(function(type) {
        return createReport(type);
      });
      form = new Form(rs);
    } else {
      report = createReport(types[0]);
    }

    // Create js Report object and set up next step.
    if (modernBrowser) {
      history.pushState({'page': 'new', 'report': report, types: types}, 'Create Report');
    }

    $("#container").addClass("rpt-container");
    if (form) {
      form.renderReports(".rpt-container");
    } else {
      report.renderFields(".rpt-container", report.fields, true);
      report.unbindEvents().bindEvents();
    }
  });

  $subpage.on("click", "#choices input[name='report']", function() {
    var $checkboxes = $("#choices input[name='report']"),
        $startReport = $("#start-report");

    if ($checkboxes.is(":checked")) {
      $startReport.removeClass("disabled");
    } else {
      $startReport.addClass("disabled");
    }
  });

  // View Report
  $subpage.on("click", ".report-row > a:not(.disabled), .fa-eye:not(.disabled), .view-report:not(.disabled)", function() {
    var reportId = $(this).parents("tr, .report-row").data("report"),
        reportName = $(this).parents("tr > td:first, .report-row").find('a').text(),
        model = $(this).parents("tr, .report-row").data("model"),
        callback = function() {
          renderNavigation(true);
        },
        views = {
          partner: function() {return renderViewPartner(reportId, reportName);},
          contact: function() {return renderViewContact(reportId, reportName);},
          contactrecord: function() {return renderGraphs(reportId, reportName, callback);}
        };

    if (modernBrowser) {
      history.pushState({page: 'view-report', model: model,
                         reportId: reportId, reportName: reportName}, 'View Report');
    }

    views[model]();
  });

  // Clone Report
  $subpage.on("click", ".fa-copy, .clone-report", function() {
    var data = {
          filters: JSON.stringify({'pk': $(this).parents("tr, .report-row").data("report")}),
          values: ['name', 'model', 'app', 'filters'],
          csrfmiddlewaretoken: readCookie("csrftoken")
        },
        url = location.protocol + "//" + location.host, // https://secure.my.jobs
        cloneReport = function() {
          $.ajax({
            type: "POST",
            url: url + "/reports/ajax/myreports/report",
            data: data,
            dataType: "json",
            success: function(data) {
              var reportData = data[0],
                  model = reportData.model,
                  filters = JSON.parse(reportData.filters),
                  report = createReport(model);

              $.extend(filters, {report_name: "Copy of " + reportData.name.replace(/_/g, " ")});

              report.createCloneReport(filters);

              $("#container").addClass("rpt-container");
              report.renderFields(".rpt-container", report.fields, true);
              report.unbindEvents().bindEvents();

              if (modernBrowser) {
                history.pushState({'page': 'clone', 'inputs': filters, 'type': report.type}, "Clone Report");
              }
            }
          });
        };

    if ($(this).attr("id") !== undefined) {
      cloneReport();
    } else {
      renderOverview(cloneReport);
    }

    navigation = true;
    renderNavigation();
  });

  $subpage.on("click", ".fa-download:not(.disabled), .export-report:not(.disabled)", function() {
    var report_id = $(this).parents("tr, .report-row").data("report");

    if (modernBrowser) {
      history.pushState({'page': 'report-download', 'report': report_id}, 'Download Report');
    }

    renderDownload(report_id);
  });

  $subpage.on("click", ".sidebar .fa-refresh:not('.fa-spin'), .regenerate-report", function() {
    var $icon = $(this),
        archive = false,
        url = location.protocol + "//" + location.host, // https://secure.my.jobs
        report_id,
        data,
        $div,
        origTitle;

    if (typeof $(this).attr("id") !== "undefined") {
      report_id = $(this).attr("id").split("-")[1];
    } else {
      $icon = $(this).children(".fa-refresh");
      $div = $(this);
      report_id = $(this).parents("tr").data("report");
      archive = true;

      if ($(this).children(".fa-spin").length) {
        return false;
      }
    }

    data = {'id': report_id};

    $.ajax({
      type: "GET",
      url: url + "/reports/ajax/regenerate",
      global: false,
      data: data,
      beforeSend: function() {
        $icon.addClass("fa-spin");
        if (archive) {
          origTitle = $div.data('original-title');
          $div.attr('data-original-title', 'Regenerating...');
          if (modernBrowser && $div.is(":hover")) {
            $div.tooltip('hide').tooltip('show');
          }
        } else {
          origTitle = $icon.data('original-title');

          // Bootstrap tooltip reads off of the attr instead of data.
          $icon.attr('data-original-title', 'Regenerating...');

          // Refresh tooltip if the user is still hovering over the element.
          if (modernBrowser && $icon.is(":hover")) {
            $icon.tooltip('hide').tooltip('show');
          }
        }
      },
      success: function() {
        $icon.removeClass("fa-spin");

        if (archive) {
          // had to select tds because editing a tr background-color does nothing.
          $div.parents('tr').children('td').effect("highlight", 600)
              .find('.export-report, .view-report').removeClass('disabled');
          $div.attr('data-original-title', origTitle);

          if (modernBrowser && $div.is(":hover")) {
            $div.tooltip('hide').tooltip('show');
          }
        } else {
          $icon.parents('div.report-row').effect("highlight", 600)
               .find('.report-link, .fa-eye, .fa-download').removeClass('disabled');
          $icon.attr('data-original-title', origTitle);

          if (modernBrowser && $icon.is(":hover")) {
            $icon.tooltip('hide').tooltip('show');
          }
        }
      }
    });
  });

  // View Archive
  $subpage.on("click", "#report-archive", function() {
    if (modernBrowser) {
      history.pushState({'page': 'report-archive'}, "Report Archive");
    }
    navigation = true;
    renderArchive(renderNavigation);
  });

  $subpage.on("click", "#reporting-version", function() {
    utils.setCookie("reporting_version", "dynamic");
    window.location.assign("/reports/view/dynamicoverview");
  });

  enableTooltips();
});


// Checks to see if browser is IE. If it is then get version.
function isIE() {
    var myNav = navigator.userAgent.toLowerCase();
    return (myNav.indexOf('msie') !== -1) ? parseInt(myNav.split('msie')[1]) : false;
}


function createReport(type) {
  var reports = {
    contact: function() {
      return new Report("contact", [new TextField({
                                          isFilter: false,
                                          label: "Report Name",
                                          id: "report_name",
                                          required: true,
                                          defaultVal: reportNameDateFormat(new Date())
                                        }),
                                    new DateField({
                                          label: "Select Date",
                                          id: "date",
                                          key: {
                                            start_date: "contactrecord.date_time.gte",
                                            end_date: "contactrecord.date_time.lte"
                                          },
                                          required: true,
                                          defaultVal: {
                                            start_date: "01/01/2014",
                                            end_date: dateFieldFormat(yesterday)
                                          }
                                        }),
                                    new StateField({
                                          label: "State",
                                          id: "state",
                                          key: "locations.state.icontains"
                                        }),
                                    new TextField({
                                          label: "City",
                                          id: "city",
                                          key: "locations.city.icontains",
                                          autofocus: 'autofocus'
                                        }),
                                    new TagField({
                                      label: "Tags",
                                      id: "tags",
                                      key: "tags.name.in",
                                      helpText: "Use commas for multiple tags."
                                    }),
                                    new FilteredList({
                                      label: "Partners",
                                      id: "partner",
                                      key: "partner.in",
                                      required: true,
                                      dependencies: {
                                        date: {
                                          start_date: 'contactrecord.date_time.gte',
                                          end_date: 'contactrecord.date_time.lte',
                                        },
                                        state: 'contact.locations.state.icontains',
                                        city: 'contact.locations.city.icontains',
                                        tags: 'contact.tags.name.in',
                                      },
                                      values: ["pk", "name"],
                                      order_by: "name"
                                    })
                                  ]);
    },
    partner: function() {
      return new Report("partner", [new TextField({
                                      isFilter: false,
                                      label: "Report Name",
                                      id: "report_name",
                                      required: true,
                                      defaultVal: reportNameDateFormat(new Date())
                                    }),
                                    new StateField({
                                      label: "State",
                                      id: "state",
                                      key: "contact.locations.state.icontains"
                                    }),
                                    new TextField({
                                      label: "City",
                                      id: "city",
                                      key: "contact.locations.city.icontains",
                                      autofocus: 'autofocus'
                                    }),
                                    new TextField({
                                      label: "URL",
                                      id: "uri",
                                      key: "uri.icontains"
                                    }),
                                    new TextField({
                                      label: "Source",
                                      id: "data_source",
                                      key: "data_source.icontains"
                                    }),
                                    new TagField({
                                      label: "Tags",
                                      id: "tags",
                                      key: "tags.name.in",
                                      helpText: "Use commas for multiple tags."
                                    })
                                  ]);
    },
    contactrecord: function() {
      var CommunicationTypeChoices = [new CheckBox({
                                  label: "Email",
                                  name: "communication_type",
                                  defaultVal: "email"
                                }),
                                new CheckBox({
                                  label: "Phone Call",
                                  name: "communication_type",
                                  defaultVal: "phone"
                                }),
                                new CheckBox({
                                  label: "Meeting or Event",
                                  name: "communication_type",
                                  defaultVal: "meetingorevent"
                                }),
                                new CheckBox({
                                  label: "Job Followup",
                                  name: "communication_type",
                                  defaultVal: "job"
                                }),
                                new CheckBox({
                                  label: "Saved Search Email",
                                  name: "communication_type",
                                  defaultVal: "pssemail"
                                })];

      return new Report("contactrecord", [new TextField({
                                            isFilter: false,
                                            label: "Report Name",
                                            id: "report_name",
                                            required: true,
                                            defaultVal: reportNameDateFormat(new Date())}),
                                          new DateField({
                                            label: "Select Date",
                                            id: "date",
                                            key: {
                                              start_date: "date_time.gte",
                                              end_date: "date_time.lte"
                                            },
                                            required: true,
                                            defaultVal: {
                                              start_date: "01/01/2014",
                                              end_date: dateFieldFormat(yesterday)
                                            }
                                          }),
                                          new StateField({
                                            label: "State",
                                            id: "state",
                                            key: "contact.locations.state.icontains"
                                          }),
                                          new TextField({
                                            label: "City",
                                            id: "city",
                                            key: "contact.locations.city.icontains",
                                            autofocus: 'autofocus'
                                          }),
                                          new CheckList({
                                            label: "Communication Types",
                                            id: "communication_type",
                                            key: "contact_type.in",
                                            required: true,
                                            defaultVal: "all",
                                            choices: CommunicationTypeChoices
                                          }),
                                          new TagField({
                                            label: "Tags",
                                            id: "tags",
                                            key: "tags.name.in",
                                            helpText: "Use commas for multiple tags."
                                          }),
                                          new FilteredList({
                                            label: "Partners",
                                            id: "partner",
                                            key: "partner.in",
                                            required: true,
                                            dependencies: {
                                              date: {
                                                start_date: 'contactrecord.date_time.gte',
                                                end_date: 'contactrecord.date_time.lte',
                                              },
                                              state: 'contact.locations.state.icontains',
                                              city: 'contact.locations.city.icontains',
                                              communication_type: 'contactrecord.contact_type.in',
                                              tags: 'contactrecord.tags.name.in',
                                            },
                                            values: ["pk", "name"],
                                            order_by: "name"
                                          }),
                                          new FilteredList({
                                            label: "Contacts",
                                            id: "contact",
                                            key: "contact.in",
                                            required: true,
                                            dependencies: {
                                              date: {
                                                start_date: 'contactrecord.date_time.gte',
                                                end_date: 'contactrecord.date_time.lte',
                                              },
                                              state: 'locations.state.icontains',
                                              city: 'locations.city.icontains',
                                              communication_type: 'contactrecord.contact_type.in',
                                              tags: 'contactrecord.tags.name.in',
                                              partner: 'partner.in'
                                            },
                                            values: ["pk", "name", "email"],
                                            order_by: "name"
                                          })
                                        ]);
    }
  };

  return reports[type]();
}


function reportNameDateFormat(date, isEndDate) {
  isEndDate = typeof isEndDate !== 'undefined' ? isEndDate : false;

  var year = date.getFullYear(),
      month = date.getMonth(),
      day = date.getDate(),
      hours = isEndDate ? 23 : date.getHours(),
      minutes = isEndDate ? 59 : date.getMinutes(),
      seconds = isEndDate ? 59 : date.getSeconds(),
      milliseconds = isEndDate ? 999 : date.getMilliseconds();

  month = turnTwoDigit(parseInt(month) + 1);
  day = turnTwoDigit(day);
  hours = turnTwoDigit(hours);
  minutes = turnTwoDigit(minutes);
  seconds = turnTwoDigit(seconds);

  return year + "-" + month + "-" + day + " " + hours + ":" + minutes + ":" + seconds + "." + milliseconds;
}


function dateFieldFormat(date) {
  var day = date.getDate(),
      month = date.getMonth(),
      year = date.getFullYear();

  day = turnTwoDigit(day);
  month = turnTwoDigit(parseInt(month) + 1);

  return month + "/" + day + "/" + year;
}


function turnTwoDigit(value) {
  return value < 10 ? "0" + value : value;
}


function pieOptions(height, width, chartArea_top, chartArea_left, chartArea_height, chartArea_width,
                    piehole_radius, slice_colors, show_tooltips) {
  var options = {legend: 'none', pieHole: piehole_radius, pieSliceText: 'none',
                 height: height, width: width,
                 chartArea: {top:chartArea_top, left:chartArea_left,
                             height: chartArea_height, width: chartArea_width},
                 slices: slice_colors
                };
  if(!show_tooltips) {
    options.tooltip = { trigger: 'none' };
  }
  return options;
}

var $navigationBar = $("#navigation");

function renderNavigation(download) {
  var mainContainer = $('#main-container'),
      $navigationBar = $navigationBar || $("#navigation");

  if (navigation) {
    if (!$navigationBar.length) {
      $navigationBar = $('<div id="navigation" class="span12" style="display:none;"></div>').append(function() {
        var $row = $('<div class="row"></div>'),
            $column1 = $('<div class="span4"></div>'),
            $column2 = $column1.clone(),
            $column3 = $column1.clone(),
            $span = $('<span id="goBack"> Back</span>'),
            $i = $('<i class="fa fa-arrow-circle-o-left fa-2x"></i>'),
            $download;

        $span.prepend($i);
        $span.on("click", function() {
          if (modernBrowser) {
            history.back();
          } else {
            renderOverview();
          }
        });
        $row.append($column1.append($span));

        if (download) {
          $download = $('<i class="fa fa-download"></i>');
          $column3.append($download);
        }

        $row.append($column2).append($column3);

        return $row;
      });
      mainContainer.prepend($navigationBar);
    }
    // TODO: Uncomment once UI for navbar is done.
    //$navigationBar.show();
  } else {
    $navigationBar.remove();
  }
}


function renderOverview(callback) {
  $.ajax({
    type: 'GET',
    url: window.location,
    data: {},
    global: false,
    success: function(data) {
      $(".subpage > .wrapper").html(data);
      enableTooltips();
    }
  }).complete(function() {
    if (typeof callback === "function") {
      return callback();
    }
  });
}

function renderDownload(report_id) {
  var data = {'id': report_id};

  $.ajax({
    type: "GET",
    url: "downloads",
    data: data,
    success: function(data) {
      var ctx,
          values,
          $order,
          $column,
          $columnNames,
          $allCheckbox,
          $checkboxes,
          $checked;

      function updateValues() {
        $checked = $(".column-container .enable-column:checked");
        $order = $(".sort-order");
        $column = $("#column-choices");
        $columnNames = $("#column-choices option:not([value=''])");

        values = $.map($checked, function(item) {
          return $(item).val();
        });

        $columnNames.each(function() {
          $(this).prop("disabled", values.indexOf($(this).val()) === -1);
        });

        ctx = {'id': report_id, 'values': values};
        if ($column.val()) {
          ctx.order_by = $order.val() + $column.val();
        }

        $("#download-csv").attr("href", "download?" + $.param(ctx));
      }

      $("#main-container").html(data);

      $allCheckbox = $(".enable-all-columns .enable-column");
      $checkboxes = $(".column-container .enable-column");
      $checked = $(".column-container .enable-column:checked");

      $allCheckbox.prop("checked", $checkboxes.length === $checked.length);
      updateValues();

      // Event Handlers
      $(".column-container").sortable({
        axis: "y",
        placeholder: "placeholder",
        containment: "parent",
        tolerance: "pointer",
        distance: 10,
        start: function(e, ui) {
          ui.item.addClass("drag");
        },
        stop: function(e, ui) {
          ui.item.removeClass("drag");
        },
        update: updateValues
      });

      $(".enable-all-columns .enable-column").on("change", function() {
        $("input.enable-column").prop("checked", $(this).is(":checked"));
      });

      $("input.enable-column").on("change", function() {
        var $checkboxes = $(".column-wrapper .enable-column"),
            $checkbox = $(this),
            $checked = $(".column-wrapper .enable-column:checked"),
            $allCheckbox = $(".enable-all-columns .enable-column"),
            $choices = $("#column-choices");

        $allCheckbox.prop("checked", $checkboxes.length === $checked.length);

        if(!$checkbox.is(":checked") && $checkbox.val() === $choices.val()) {
          $choices.val("");
        }
      });

      $("#download-cancel").on("click", function() {
        if (modernBrowser) {
          history.back();
        } else {
          renderOverview();
        }
      });

      $("#column-choices").on("change", updateValues);
      $(".sort-order").on("change", updateValues);

      $(".enable-column").on("change", function() {
        updateValues();
      });
    }
  });
}


function renderGraphs(report_id, reportName, callback, overrideUrl) {
  var data = {'id': report_id},
      url = location.protocol + "//" + location.host; // https://secure.my.jobs

  navigation = true;

  $.ajax({
    type: "GET",
    url: url + (overrideUrl ? overrideUrl : "/reports/view/mypartners/contactrecord"),
    data: data,
    success: function(data) {
      var contacts = data.contacts,
          communications = data.communications || 0,
          emails = data.emails || 0,
          pss = data.searches || 0,
          calls = data.calls || 0,
          meetings = data.meetings || 0,
          referrals = data.referrals || 0,
          applications = data.applications || 0,
          interviews = data.interviews || 0,
          hires = data.hires || 0,
          pChartInfo = {0: {'name': "Emails",            'count': emails,   'color': "#5EB95E"},
                        1: {'name': "PSS Emails",        'count': pss,      'color': "#4BB1CF"},
                        2: {'name': "Phone Calls",       'count': calls,    'color': "#FAA732"},
                        3: {'name': "Meetings & Events", 'count': meetings, 'color': "#5F6C82"}},
          bChartInfo = {0: {'name': "Applications", 'count': applications, 'style': "color: #5EB95E"},
                        1: {'name': "Interviews",   'count': interviews,   'style': "color: #4BB1CF"},
                        2: {'name': "Hires",        'count': hires,        'style': "color: #FAA732"},
                        3: {'name': "Records",      'count': referrals,    'style': "color: #5F6C82"}};

      // Grab google's jsapi to load chart files.
      $.getScript("https://www.google.com/jsapi", function() {
        // Had to use 'callback' with google.load otherwise after load google makes a new document
        // with just <html> tags.
        google.load("visualization", "1.0", {'packages':["corechart"], 'callback': function() {
          var pDataTable = [['Records', 'All Records']], // p for pieChart
              bDataTable = [['Activity', 'Amount', {'role': 'style'}]], // b for barChart
              $mainContainer = $("#main-container"),// the container everything goes in
              pSliceOptions = {}, // slice options for pieChart
              pLegend = [], // array that will hold the report-boxes for pieChart
              bLegend = [], // array that will hold the report-boxes for barChart
              pChartData,
              pKey,
              pValue,
              pBox,
              pOptions,
              pChart,
              $pLegend,
              $pChart,
              bChartData,
              bValue,
              bKey,
              bBox,
              bOptions,
              bChart,
              $bLegend,
              topThreeRow,
              restRow,
              contactContainer,
              i;

          $mainContainer.html('').append("<div class='span12 col-sm-12'><h2>" + reportName + "</h2></div>" +
                                         "<div class='span6 col-sm-12'><h4>Communication Activity</h4><div id='d-chart'></div>" +
                                         "</div><div class='span6 col-sm-12'><h4>Referral Activity</h4><div id='b-chart'></div></div>");

          for (pKey in pChartInfo) {
            if (pChartInfo.hasOwnProperty(pKey)) {
              pValue = pChartInfo[pKey];
              pDataTable.push([pValue.name, pValue.count]);

              // Used for PieChart to give data 'slices' color.
              pSliceOptions[pKey] = {'color': pValue.color};

              // Create legend boxes
              pBox = $('<div class="report-box" style="background-color: ' +
                       pValue.color + '"><div class="big-num">' + pValue.count +
                       '</div><div class="reports-record-type">' + pValue.name + '</div></div>');
              pLegend.push(pBox);
            }
          }

          pChartData = google.visualization.arrayToDataTable(pDataTable);
          pOptions = pieOptions(330, 350, 12, 12, 300, 330, 0.6, pSliceOptions, true);
          pChart = new google.visualization.PieChart(document.getElementById('d-chart'));
          pChart.draw(pChartData, pOptions);

          $pChart = $("#d-chart > div");
          $pChart.append("<div class='chart-box-holder legend'></div>");
          $pLegend = $("#d-chart .legend");
          pLegend.forEach(function(element) {
            $pLegend.append(element);
          });

          $pChart.append('<div class="piehole report"><div class="piehole-big">' + communications +
                         '</div><div class="piehole-topic">Communication Records</div></div>');

          for (bKey in bChartInfo) {
            if (bChartInfo.hasOwnProperty(bKey)) {
              bValue = bChartInfo[bKey];
              bDataTable.push([bValue.name, bValue.count, bValue.style]);

              bBox = $('<div class="report-box" style="background-' + bValue.style +
                       '"><div class="big-num">' + bValue.count +
                       '</div><div class="reports-record-type">' + bValue.name + '</div></div>');
              bLegend.push(bBox);
            }
          }

          bChartData = google.visualization.arrayToDataTable(bDataTable);
          bOptions = {title: 'Referral Records', width: 356, height: 360, legend: { position: "none" },
                      chartArea: {top: 22, left: 37, height: 270, width: 290},
                      animation: {startup: true, duration: 400}};
          bChart = new google.visualization.ColumnChart(document.getElementById('b-chart'));
          bChart.draw(bChartData, bOptions);

          $bLegend = $('<div class="chart-box-holder legend"></div>').append(function() {
            return bLegend.map(function(element) {
              return element.prop("outerHTML");
            }).join('');
          });

          $("#b-chart > div").append($bLegend);

          // Show the top three contacts in a different format than the rest.
          topThreeRow = $('<div class="row"></div>').append(function() {
            var html = '',
                cLength = contacts.length,
                contact,
                name,
                email,
                cReferrals,
                commRecords,
                div,
                topLength;

            // Determine how long topLength should be.
            topLength = (cLength > 3) ? 3 : cLength;

            // Just run for the first 3 contacts.
            for (i = 0; i < topLength; i++) {
              // remove first contact in array, returns the removed contact.
              contact = contacts[i];
              name = contact.contact__name;
              email = contact.contact_email;
              cReferrals = contact.referrals;
              commRecords = contact.records;

              // create container
              div = $('<div class="span4 col-md-4 col-sm-12 top-contacts"></div>');
              div.append('<div class="panel">' +
                         '<div class="name">' + name + '</div><div class="email">' + email + '</div><div class="top-three-box-container">' +
                         '<div class="report-box small"><div class="big-num">' + commRecords +
                         '</div><div class="reports-record-type">Communication Records</div></div>' +
                         '<div class="report-box small"><div class="big-num">' + cReferrals +
                         '</div><div class="reports-record-type">Referral Records</div></div></div>' +
                         '</div>');

              // add the rendered html as a string.
              html += div.prop("outerHTML");
            }
            return html;
          });

          // Don't generate a table if cLength = 0
          if (contacts.length) {
            restRow = $('<div class="row"></div>').append(function() {
              var div = $('<div class="span12 col-sm-12"></div>'),
                  table = $('<table class="table table-striped report-table"><thead><tr><th>Name</th>' +
                            '<th>Email</th><th>Partner</th><th>Communication Records</th><th>Referral Records</th>' +
                            '</tr></thead></table>'),
                  tbody = $('<tbody></tbody>');
              tbody.append(function() {
                // turn each element into cells of a table then join each group of cells with rows.
                return "<tr class='report'>" + contacts.map(function(contact) {
                  return "<td data-name='" + contact.contact__name + "' data-email='" + contact.contact_email + "' data-partner='" + contact.partner + "'>" + contact.contact__name + "</td><td>" + contact.contact_email +
                         "</td><td>" + contact.partner__name + "</td><td>" + contact.records + "</td><td>" + contact.referrals + "</td>";
                }).join('</tr><tr class="report">') + "</tr>";
              });
              tbody.find("tr").on("click", function(e) {
                var row = e.currentTarget,
                    $td = $(row).find("td:first"),
                    name = $td.data("name"),
                    email = $td.data("email"),
                    partner = $td.data("partner");

                window.open("/prm/view/records?partner=" + partner + "&contact=" + name + "&keywords=" + email, "_blank");
              });

              return div.append(table.append(tbody));

            });
          } else {
            // Make sure topThreeRow didn't run before saying there are no records.
            if (topThreeRow.find("div.top-contacts").length === 0) {
              restRow = $('<div class="row"><div class="span12">This report has no contacts with records.</div></div>');
            }
          }

          contactContainer = $('<div id="report-contacts" class="span12"></div>').append(topThreeRow).append(restRow);
          $("#main-container").append(contactContainer);

          if (typeof callback === "function") {
            callback();
          }
        }});
      });
    }
  });
}


function renderViewPartner(id, name, overrideUrl) {
  var data = {id: id},
      url = location.protocol + "//" + location.host; // https://secure.my.jobs

  $.ajax({
    type: "GET",
    url: url + (overrideUrl ? overrideUrl : "/reports/view/mypartners/partner"),
    data: data,
    success: function(data) {
      var $span = $('<div class="span12 col-sm-12"><h2>' + name + '</h2></div>'),
          $table = $('<table class="table table-striped report-table"><thead><tr>' +
                     '<th>Name</th><th>Primary Contact</th></tr></thead></table>'),
          $tbody = $('<tbody></tbody>'),
          $mainContainer = $("#main-container");

      $tbody.append(function() {
        return '<tr class="record">' + data.map(function(record) {
            return '<td>' + record.name + '</td><td>' + record.primary_contact + '</td>';
          }).join('</tr><tr>') + '</tr>';
      });

      $mainContainer.html("").append($span.append($table.append($tbody)));
    }
  });
}


function renderViewContact(id, name, overrideUrl) {
   var data = {id: id},
      url = location.protocol + "//" + location.host; // https://secure.my.jobs

  $.ajax({
    type: "GET",
    url: url + (overrideUrl ? overrideUrl : "/reports/view/mypartners/contact"),
    data: data,
    success: function(data) {
      var $span = $('<div class="span12 col-sm-12"><h2>' + name + '</h2></div>'),
          $table = $('<table class="table table-striped report-table"><thead><tr>' +
                     '<th>Partner</th><th>Name</th><th>Phone</th><th>Email</th><th>State(s)</th></tr></thead></table>'),
          $tbody = $('<tbody></tbody>'),
          $mainContainer = $("#main-container"),
          location;

      // Append content to Table's tbody.
      $tbody.append('<tr class="record">' + data.map(function(record) {
        // Create a list of States based off of locations
        // in a format of City, State, or objects shaped like
        // {city: '', state: ''}
        location = record.locations.map(function(location) {
            // for each location get state and trim whitespace
            if (typeof(location) === 'string') {
                return (location.split(',')[1] || '').trim();
            } else if (typeof(location) === 'object') {
                return location.state.trim();
            }
            // Determine uniqueness
          }).sort().filter(function(e, i, a) {
            // Due to sort, duplicates will be together.
            // Check to see if this element is not the same as the prior one.
            return e !== a[i - 1];
          }).join(', ');

        return '<td>' + record.partner + '</td><td>' + record.name + '</td><td>' + record.phone + '</td>' +
               '<td>' + record.email + '</td><td>' + location + '</td>';
        }).join('</tr><tr>') + '</tr>'
      );

      $mainContainer.html("").append($span.append($table.append($tbody)));
    }
  });
}


function renderArchive(callback) {
  $.ajax({
    type: "GET",
    url: "archive",
    data: {},
    success: function(data) {
      $("#main-container").html(data);
      enableTooltips();
    }
  }).complete(function() {
    if (typeof callback === "function") {
      callback();
    }
  });
}


function enableTooltips() {
  // Enable bootstrap tooltips
  $('[data-toggle="tooltip"]').tooltip();
}
