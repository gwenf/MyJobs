import React, {Component, PropTypes} from 'react';
import {map} from 'lodash-compat/collection';
import {calendarDays} from 'common/calendar-support';
import Select from 'common/ui/Select';
import classnames from 'classnames';

export default class CalendarPanel extends Component {
  renderDayHeader(name) {
    return (
      <th key={name}>{name}</th>
    );
  }

  renderDay(day) {
    const {onSelect} = this.props;
    const className = classnames({
      dim: day.siblingMonth,
      selected: day.selected,
      'in-range': day.inRange,
    });
    const dayEvent = {year: day.year, month: day.month, day: day.day};
    return (
      <td
        key={day.day}
        className={className}
        onClick={() => onSelect(dayEvent)}>
        {day.day}
      </td>
    );
  }

  render() {
    const {
      year,
      month,
      selectedDate,
      otherDate,
      yearChoices,
      monthChoices,
      onYearChange,
      onMonthChange,
    } = this.props;
    const weeks = calendarDays(year, month, selectedDate, otherDate);
    const dayNames = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];
    return (
      <div className="calendar-panel">
        <div className="row">
          <div className="col-xs-6">
            <Select
              name="year"
              initial={year.toString()}
              choices={yearChoices}
              onChange={e => onYearChange(e.target.value)}
              />
          </div>
          <div className="col-xs-6">
            <Select
              name="month"
              initial={month.toString()}
              choices={monthChoices}
              onChange={e => onMonthChange(e.target.value)}
              />
          </div>
        </div>
        <table className="calendar-table">
          <thead>
            <tr>
              {map(dayNames, n => this.renderDayHeader(n))}
            </tr>
          </thead>
          <tbody>
          { map(weeks, (week, i) => (
            <tr key={i}>
              {map(week, day => this.renderDay(day))}
            </tr>
          ))}
          </tbody>
        </table>
      </div>
    );
  }
}

CalendarPanel.defaultProps = {
  yearChoices: [
    {value: 2008, display: '2008'},
    {value: 2009, display: '2009'},
    {value: 2010, display: '2010'},
    {value: 2011, display: '2011'},
    {value: 2012, display: '2012'},
    {value: 2013, display: '2013'},
    {value: 2014, display: '2014'},
    {value: 2015, display: '2015'},
    {value: 2016, display: '2016'},
    {value: 2017, display: '2017'},
    {value: 2018, display: '2018'},
    {value: 2019, display: '2019'},
    {value: 2020, display: '2020'},
  ],
  monthChoices: [
    {value: 0, display: 'January'},
    {value: 1, display: 'February'},
    {value: 2, display: 'March'},
    {value: 3, display: 'April'},
    {value: 4, display: 'May'},
    {value: 5, display: 'June'},
    {value: 6, display: 'July'},
    {value: 7, display: 'August'},
    {value: 8, display: 'September'},
    {value: 9, display: 'October'},
    {value: 10, display: 'November'},
    {value: 11, display: 'December'},
  ],
  selectedDate: null,
  otherDate: null,
  selectBefore: false,
  selectAfter: false,
};

CalendarPanel.propTypes = {
  year: PropTypes.number.isRequired,
  yearChoices: React.PropTypes.arrayOf(
    React.PropTypes.shape({
      value: React.PropTypes.any.isRequired,
      display: React.PropTypes.string.isRequired,
    })
  ),
  month: PropTypes.number.isRequired,
  monthChoices: React.PropTypes.arrayOf(
    React.PropTypes.shape({
      value: React.PropTypes.any.isRequired,
      display: React.PropTypes.string.isRequired,
    })
  ),

  selectedDate: PropTypes.shape({
    year: PropTypes.number.isRequired,
    month: PropTypes.number.isRequired,
    day: PropTypes.number.isRequired,
  }),
  otherDate: PropTypes.shape({
    year: PropTypes.number.isRequired,
    month: PropTypes.number.isRequired,
    day: PropTypes.number.isRequired,
  }),

  selectBefore: PropTypes.bool,
  selectAfter: PropTypes.bool,

  onSelect: PropTypes.func.isRequired,
  onYearChange: PropTypes.func.isRequired,
  onMonthChange: PropTypes.func.isRequired,
};
