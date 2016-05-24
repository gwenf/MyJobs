import React from 'react';
import TextField from './TextField';
import CalendarPanel from './CalendarPanel';
import ClickOutCompat from 'common/ui/ClickOutCompat';
import moment from 'moment';

/**
 * DateField.jsx is a textbox with a calendar button. The button launches the
 * popup calendar CalendarPanel.jsx.
 *
 * To use in an app, pass in onChange as a callback. Detect which element (e.g.
 * day, month, year) was changed by checking event.target.type. For example,
 * if the user selects a day then event.target.type === 'calendar-day'.
 *
 * The selected value is in event.target.value.
 */

class DateField extends React.Component {
  constructor(props) {
    super(props);
    let year;
    let month;
    let day;
    const value = this.props.value;
    if (value) {
      const momentObject = moment(value, 'YYYY-MM-DD');
      day = momentObject.date();
      month = momentObject.month();
      year = momentObject.year();
    }
    this.state = {
      year: year,
      month: month,
      day: day,
      displayCalendar: false,
      dateInvalid: false,
    };
  }
  onInputBlur() {
    const {mouseInCalendar} = this.state;
    if (!mouseInCalendar) {
      this.closeCalendar();
    }
  }
  onMouseInCalendar(value) {
    this.setState({mouseInCalendar: value});
  }
  onDaySelect(day) {
    this.updateDay(day);
    this.closeCalendar();
  }
  updateDay(day) {
    const {onChange, value} = this.props;

    if (!moment(value, 'MM/DD/YYYY', true).isValid()) {
      this.resetDateToNow();
    }

    const fakeEvent = {};
    fakeEvent.target = {};
    fakeEvent.target.name = this.props.name;
    fakeEvent.target.type = 'calendar-day';
    fakeEvent.target.value = day.day;
    onChange(fakeEvent);
  }
  updateMonth(month) {
    const {onChange, value} = this.props;

    if (!moment(value, 'MM/DD/YYYY', true).isValid()) {
      this.resetDateToNow();
    }

    const fakeEvent = {};
    fakeEvent.target = {};
    fakeEvent.target.name = this.props.name;
    fakeEvent.target.type = 'calendar-month';
    fakeEvent.target.value = month;
    onChange(fakeEvent);
  }
  updateYear(year) {
    const {onChange, value} = this.props;

    if (!moment(value, 'MM/DD/YYYY', true).isValid()) {
      this.resetDateToNow();
    }

    const fakeEvent = {};
    fakeEvent.target = {};
    fakeEvent.target.name = this.props.name;
    fakeEvent.target.type = 'calendar-year';
    fakeEvent.target.value = year;
    onChange(fakeEvent);
  }
  generateYearChoices(numberOfYears) {
    const now = new Date();
    const currentYear = now.getFullYear();

    const yearChoices = [];
    for (let i = 0; i < numberOfYears; i++) {
      yearChoices.push({value: (currentYear - i), display: (currentYear - i).toString()});
    }
    return yearChoices;
  }
  closeCalendar() {
    this.setState({displayCalendar: false});
  }
  resetDateToNow() {
    let year;
    let month;
    let day;

    const {onChange} = this.props;
    const now = new Date();
    month = (now.getMonth() + 1) < 10 ? '0' + (now.getMonth() + 1) : (now.getMonth() + 1);
    day = now.getDate() < 10 ? '0' + now.getDate() : now.getDate();
    year = now.getFullYear();

    const newDate = month + '/' + day + '/' + year;

    const fakeEvent = {};
    fakeEvent.target = {};
    fakeEvent.target.name = this.props.name;
    fakeEvent.target.type = 'entire-date';
    fakeEvent.target.value = newDate;
    onChange(fakeEvent);
  }
  openCalendar() {
    const {value} = this.props;
    // Check if date is valid
    // If not, replace with what it was on page load (what was passed in or today's date
    if (!moment(value, 'MM/DD/YYYY', true).isValid()) {
      this.resetDateToNow();
    }
    this.setState({displayCalendar: true});
  }
  toggleCalendar() {
    if (this.state.displayCalendar) {
      this.closeCalendar();
    } else {
      this.openCalendar();
    }
  }
  render() {
    const {
      name,
      onChange,
      required,
      maxLength,
      isHidden,
      value,
      placeholder,
      error} = this.props;

    let momentObject = moment(value, 'MM/DD/YYYY');
    let day;
    let month;
    let year;

    // Handle error message
    let errorMessage;
    if (error) {
      errorMessage = error;
    }

    // Date value must match our custom format (not ISO 8601)
    if (moment(value, 'MM/DD/YYYY', true).isValid()) {
      momentObject = moment(value, 'MM/DD/YYYY');
      day = momentObject.date();
      month = momentObject.month();
      year = momentObject.year();
    } else {
      errorMessage = 'Date error. Must be of format: MM/DD/YYYY';
      day = 0;
      month = 1;
      year = 2000;
    }

    let errorComponent;
    if (errorMessage) {
      errorComponent = (
        <div className="error-text">{errorMessage}</div>
      );
    }

    let calendar;
    if (this.state.displayCalendar) {
      calendar = (<div className="input-group datepicker-dropdown dropdown-menu"
                    onMouseEnter={() => this.onMouseInCalendar(true)}
                    onMouseLeave={() => this.onMouseInCalendar(false)}>
                    <CalendarPanel
                      year={year}
                      month={month}
                      day={day}
                      onYearChange={y => this.updateYear(y)}
                      onMonthChange={m => this.updateMonth(m)}
                      onSelect={d => this.onDaySelect(d)}
                      closeCalendar={() => this.closeCalendar()}
                      yearChoices={this.generateYearChoices(50)}
                      />
                  </div>);
    }

    return (
      <ClickOutCompat onClickOut={e => this.closeCalendar(e, this)}>
        <div>
          <TextField
            id={name}
            name={name}
            className="datepicker-input"
            maxLength={maxLength}
            required={required}
            hidden={isHidden}
            value={value}
            placeholder={placeholder}
            onChange={onChange}
            onFocus={e => this.toggleCalendar(e, this)}
            onBlur={e => this.onInputBlur(e)}
          />
        </div>
        {errorComponent}
        {calendar}
      </ClickOutCompat>
    );
  }
}

DateField.propTypes = {
  /**
  * Callback: the user edited this field
  *
  * obj: change event
  */
  onChange: React.PropTypes.func.isRequired,
  /**
   * under_score_seperated, unique name of this field. Used to post form
   * content to Django
   */
  name: React.PropTypes.string.isRequired,
  /**
   * Placeholder text for the input control
   */
  placeholder: React.PropTypes.string,
  /**
   * Value at first page load
   */
  value: React.PropTypes.string,
  /**
   * Number of characters allowed in this field
   */
  maxLength: React.PropTypes.number,
  /**
   * Should this component be shown or not?
   */
  isHidden: React.PropTypes.bool,
  /**
   * Must this field have a value before submitting form?
   */
  required: React.PropTypes.bool,
  /**
   * Should this bad boy focus, all auto like?
   */
  autoFocus: React.PropTypes.string,
  /**
   * Validation error
   */
  error: React.PropTypes.string,
};

DateField.defaultProps = {
  placeholder: '',
  value: '',
  maxLength: null,
  isHidden: false,
  required: false,
  autoFocus: '',
  error: null,
};

export default DateField;
