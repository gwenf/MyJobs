import {calendarDays} from '../calendar-support';

describe('Calendar', () => {
  it('spits out arrays of days', () => {
    const weeks = calendarDays(2016, 2);
    expect(weeks[0][1]).toEqual(jasmine.objectContaining({
      year: 2016,
      month: 2,
      day: 1,
    }));
  });

  it('adds a selected attribute', () => {
    const selected = {
      year: 2016,
      month: 2,
      day: 5,
    };
    const weeks = calendarDays(2016, 2, selected);
    expect(weeks[0][5]).toEqual(jasmine.objectContaining({
      day: 5,
      selected: true,
    }));
  });

  it('handles an "other" attribute when other is later than selected', () => {
    const selected = {
      year: 2016,
      month: 2,
      day: 5,
    };
    const other = {
      year: 2016,
      month: 2,
      day: 10,
    };
    const weeks = calendarDays(2016, 2, selected, other);
    expect(weeks[0][4]).toEqual(jasmine.objectContaining({
      day: 4,
      inRange: false,
      selected: false,
    }));
    expect(weeks[0][5]).toEqual(jasmine.objectContaining({
      day: 5,
      inRange: true,
      selected: true,
    }));
    expect(weeks[1][0]).toEqual(jasmine.objectContaining({
      day: 7,
      inRange: true,
      selected: false,
    }));
    expect(weeks[1][3]).toEqual(jasmine.objectContaining({
      day: 10,
      inRange: true,
      selected: false,
    }));
  });

  it('handles an "other" attribute when other is earlier than selected', () => {
    const selected = {
      year: 2016,
      month: 2,
      day: 10,
    };
    const other = {
      year: 2016,
      month: 2,
      day: 5,
    };
    const weeks = calendarDays(2016, 2, selected, other);
    expect(weeks[0][4]).toEqual(jasmine.objectContaining({
      day: 4,
      inRange: false,
      selected: false,
    }));
    expect(weeks[0][5]).toEqual(jasmine.objectContaining({
      day: 5,
      inRange: true,
      selected: false,
    }));
    expect(weeks[1][0]).toEqual(jasmine.objectContaining({
      day: 7,
      inRange: true,
      selected: false,
    }));
    expect(weeks[1][3]).toEqual(jasmine.objectContaining({
      day: 10,
      inRange: true,
      selected: true,
    }));
  });

  it('handles an "other" attribute when other is equal to selected', () => {
    const selected = {
      year: 2016,
      month: 2,
      day: 5,
    };
    const other = {
      year: 2016,
      month: 2,
      day: 5,
    };
    const weeks = calendarDays(2016, 2, selected, other);
    expect(weeks[0][4]).toEqual(jasmine.objectContaining({
      day: 4,
      inRange: false,
      selected: false,
    }));
    expect(weeks[0][5]).toEqual(jasmine.objectContaining({
      day: 5,
      selected: true,
      inRange: true,
    }));
    expect(weeks[0][6]).toEqual(jasmine.objectContaining({
      day: 6,
      inRange: false,
      selected: false,
    }));
  });
});

