import React, {PropTypes, Component} from 'react';
import {map} from 'lodash-compat';

import CalendarPanel from 'common/ui/CalendarPanel';

export default class CalendarPanelTest extends Component {
  constructor() {
    super();
    const now = new Date();
    this.state = {
      year: now.getFullYear(),
      month: now.getMonth(),
      selectedDate: null,
      selectEvents: [],
    };
  }

  onDaySelect(day) {
    const {selectEvents} = this.state;
    selectEvents.unshift(day);
    const newSelectEvents = [...selectEvents];
    this.setState({
      selectEvents: newSelectEvents,
      selectedDate: day,
    });
  }

  render() {
    const {
      year,
      month,
      selectEvents,
      selectedDate,
    } = this.state;
    return (
      <div>
        <CalendarPanel
          year={year}
          month={month}
          onYearChange={y => this.setState({year: y})}
          onMonthChange={m => this.setState({month: m})}
          selectedDate={selectedDate}
          otherDate={{year: 2016, month: 2, day: 2}}
          onSelect={d => this.onDaySelect(d)}
          />
        {map(selectEvents, (d, i) => (
          <div key={i}>{JSON.stringify(d)}</div>
        ))}
      </div>
    );
  }
}
