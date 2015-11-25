import React, {PropTypes, Component} from 'react';
import Autosuggest from 'react-autosuggest';
import {Button, Glyphicon} from 'react-bootstrap';


// Future: factor out components likely to be useful and move them to a
// module suitable for sharing between apps.

class Link extends Component {
  linkClick(e) {
    e.preventDefault();
    this.props.linkClick();
  }

  render() {
    return (
      <a className="" href="#" onClick={e => this.linkClick(e)}>
        {this.props.label}
      </a>
    );
  }
}

Link.propTypes = {
  linkClick: PropTypes.func.isRequired,
  label: PropTypes.string.isRequired,
};


function LinkRow(props) {
  return (
    <div className="row">
      <div className="span2" style={{textAlign: 'right'}}>
        <Link
          linkClick={() => props.linkClick(props.id)}
          label={props.label}/>
      </div>
      <div className="span4">{props.text}</div>
    </div>
  );
}

LinkRow.propTypes = {
  linkClick: PropTypes.func.isRequired,
  text: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
};


export function WizardPageReportingTypes(props) {
  const data = props.data;
  const rows = Object.keys(data).map(k =>
    <LinkRow key={k} id={k} label={data[k].name}
      text={data[k].description}
      linkClick={() => props.selected(k)}/>
  );

  return (
    <div>
      <div className="row">
        <div className="span2" style={{textAlign: 'right'}}>
        </div>
        <div className="span4">
          <h4>Reporting Types</h4>
        </div>
      </div>
      {rows}
    </div>
  );
}

WizardPageReportingTypes.propTypes = {
  data: PropTypes.object.isRequired,
  selected: PropTypes.func.isRequired,
};


export function WizardPageReportTypes(props) {
  const data = props.data;
  const rows = Object.keys(data).map(k =>
    <LinkRow key={k} id={k} label={data[k].name}
      text={data[k].description}
      linkClick={() => props.selected(k)}/>
  );

  return (
    <div>
      <div className="row">
        <div className="span2" style={{textAlign: 'right'}}>
        </div>
        <div className="span4">
          <h4>Report Types</h4>
        </div>
      </div>
      {rows}
    </div>
  );
}

WizardPageReportTypes.propTypes = {
  data: PropTypes.object.isRequired,
  selected: PropTypes.func.isRequired,
};


export function WizardPageDataTypes(props) {
  const data = props.data;
  const rows = Object.keys(data).map(k =>
    <LinkRow key={k} id={k} label={data[k].name}
      text={data[k].description}
      linkClick={() => props.selected(k)}/>
  );

  return (
    <div>
      <div className="row">
        <div className="span2" style={{textAlign: 'right'}}>
        </div>
        <div className="span4">
          <h4>Data Types</h4>
        </div>
      </div>
      {rows}
    </div>
  );
}

WizardPageDataTypes.propTypes = {
  data: PropTypes.object.isRequired,
  selected: PropTypes.func.isRequired,
};


export function WizardPagePresentationTypes(props) {
  const data = props.data;
  const rows = Object.keys(data).map(k =>
    <div key={k} className="row">
      <div className="span2" style={{textAlign: 'right'}}>
      </div>
      <div className="span4">
        <Link id={k} label={data[k].name}
          linkClick={() => props.selected(k)}/>
      </div>
    </div>
  );

  return (
    <div>
      <div className="row">
        <div className="span2" style={{textAlign: 'right'}}>
        </div>
        <div className="span4">
          <h4>Presentation Types</h4>
        </div>
      </div>
      {rows}
    </div>
  );
}

WizardPagePresentationTypes.propTypes = {
  data: PropTypes.object.isRequired,
  selected: PropTypes.func.isRequired,
};

export class WizardPageFilter extends Component {
  componentDidMount() {
    this.updateState();
  }

  async getHints(filter, partial) {
    const {reportConfig} = this.props;
    return await reportConfig.getHints(filter, partial);
  }

  updateFilter(filter, value) {
    const {reportConfig} = this.props;
    reportConfig.setFilter(filter, value);
    this.updateState();
  }

  addToMultifilter(filter, value) {
    const {reportConfig} = this.props;
    reportConfig.addToMultifilter(filter, value);
    this.updateState();
  }

  removeFromMultifilter(filter, value) {
    const {reportConfig} = this.props;
    reportConfig.removeFromMultifilter(filter, value);
    this.updateState();
  }

  updateState() {
    const {reportConfig} = this.props;
    this.setState({
      filter: reportConfig.getFilter(),
    });
  }

  renderRow(displayName, key, content) {
    return (
      <div key={key} className="row">
        <div className="span2" style={{textAlign: 'right'}}>
          {displayName}
        </div>
        <div className="span5">
          {content}
        </div>
      </div>
    );
  }

  render() {
    const {reportConfig} = this.props;

    const rows = [];
    reportConfig.filters.forEach(col => {
      switch (col.interface_type) {
      case 'date_range':
        rows.push(this.renderRow(col.display, col.filter,
          <WizardFilterDateRange
            id={col.filter}
            updateFilter={v =>
              this.updateFilter(col.filter, v)}/>
        ));
        break;
      case 'search_select':
        rows.push(this.renderRow(col.display, col.filter,
          <WizardFilterSearchDropdown
            id={col.filter}
            updateFilter={v =>
              this.updateFilter(col.filter, v)}
            getHints={v =>
              this.getHints(col.filter, v)}/>
        ));
        break;
      case 'city_state':
        rows.push(this.renderRow(col.display, col.filter,
          <WizardFilterCityState
            id={col.filter}
            updateFilter={v =>
              this.updateFilter(col.filter, v)}
            getHints={(f, v) =>
              this.getHints(f, v)}/>
        ));
        break;
      case 'search_multiselect':
        rows.push(this.renderRow(col.display, col.filter,
          <WizardFilterMultiCollect
            id={col.filter}
            addItem={v =>
              this.addToMultifilter(col.filter, v)}
            getHints={v =>
              this.getHints(col.filter, v)}/>
        ));
        rows.push(this.renderRow(
          '',
          col.filter + '-selected',
          <WizardFilterCollectedItems
            items={
              reportConfig.getMultiFilter(col.filter)
                || []
            }
            remove={v =>
              this.removeFromMultifilter(
                col.filter,
                v)}/>));
        break;
      }
    });

    return (
      <form>
        {this.renderRow('', 'head', <h2>Set Up Report</h2>)}
        <hr/>
        {rows}
        <hr/>
        {this.renderRow('', 'submit',
          <Button
            onClick={() => reportConfig.run()}>
            Run Report
          </Button>)}

      </form>
    );
  }
}

WizardPageFilter.propTypes = {
  reportConfig: PropTypes.object.isRequired,
};


export class WizardFilterCityState extends Component {
    constructor() {
      super();
      this.state = {city: '', state: ''};
    }

    updateField(field, value) {
      const {updateFilter} = this.props;
      const newState = {...this.state};
      newState[field] = value;
      this.setState(newState);
      updateFilter(newState);
    }

    render() {
      const {id, getHints} = this.props;
      return (
        <span>
          <WizardFilterSearchDropdown
            id={id + '-city'}
            placeholder="city"
            updateFilter={v =>
              this.updateField('city', v)}
            getHints={v =>
              getHints('city', v)}/>
          <WizardFilterSearchDropdown
            id={id + '-state'}
            placeholder="state"
            updateFilter={v =>
              this.updateField('state', v)}
            getHints={v =>
              getHints('state', v)}/>
        </span>
      );
    }

}

WizardFilterCityState.propTypes = {
  id: PropTypes.string.isRequired,
  updateFilter: PropTypes.func.isRequired,
  getHints: PropTypes.func.isRequired,
};


export class WizardFilterDateRange extends Component {
    constructor() {
      super();
      this.state = {begin: '', end: ''};
    }

    updateField(field, value) {
      const {updateFilter} = this.props;
      const newState = {...this.state};
      newState[field] = value;
      this.setState(newState);
      updateFilter([newState.begin, newState.end]);
    }

    render() {
      return (
        <span>
          <div>
            <input
              type="text"
              placeholder="begin date"
              onChange={e =>
                this.updateField('begin', e.target.value)} />
          </div>
          <div>
            <input
              type="text"
              placeholder="end date"
              onChange={e =>
                this.updateField('end', e.target.value)} />
          </div>
        </span>
      );
    }

}

WizardFilterDateRange.propTypes = {
  id: PropTypes.string.isRequired,
  updateFilter: PropTypes.func.isRequired,
};


export class WizardFilterSearchDropdown extends Component {
  async loadOptions(input, cb) {
    const {getHints} = this.props;
    const hints = await getHints(input);
    cb(null, hints);
  }

  suggestionRenderer(suggestion) {
    return (
      <a href="#">
        {suggestion.display}
      </a>
    );
  }

  render() {
    const {id, updateFilter, placeholder} = this.props;
    const eid = 'filter-autosuggest-' + id;

    return (
      <Autosuggest
        id={eid}
        cache={false}
        suggestions={(input, cb) =>
          this.loadOptions(input, cb)}
        suggestionRenderer={(s, i) =>
          this.suggestionRenderer(s, i)}
        suggestionValue={s => s.key}
        theme={{
          root: 'dropdown open',
          suggestions: 'dropdown-menu',
        }}
        inputAttributes={{
          type: 'search',
          placeholder: placeholder,
          onChange: v => updateFilter(v),
        }}/>
    );
  }
}

WizardFilterSearchDropdown.propTypes = {
  id: PropTypes.string.isRequired,
  updateFilter: PropTypes.func.isRequired,
  getHints: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
};


export class WizardFilterMultiCollect extends Component {
    constructor() {
      super();
      this.state = { value: '' };
    }

    componentDidMount() {
      this.updateState('');
    }

    onInputChange(value) {
      this.updateState(value);
    }

    updateState(value) {
      this.setState({value: value});
    }

    async loadOptions(input, cb) {
      const {getHints} = this.props;
      const hints = await getHints(input);
      cb(null, hints);
    }

    selectOption(value, event) {
      const {addItem} = this.props;
      event.preventDefault();
      addItem(value);
        // Shouldn't have to do this delay but for some reason
        // we need it if the user reached here by clicking.
      setTimeout(() => this.updateState(''), 300);
    }

    suggestionRenderer(suggestion) {
      return (
        <a href="#">
          {suggestion.display}
        </a>
      );
    }

    render() {
      const {id} = this.props;
      const {value} = this.state;
      const eid = 'filter-autosuggest-' + id;

      return (
        <Autosuggest
          id={eid}
          cache={false}
          value={value}
          suggestions={(input, cb) =>
            this.loadOptions(input, cb)}
          suggestionRenderer={(s, i) =>
            this.suggestionRenderer(s, i)}
          suggestionValue={s => s.key.toString()}
          theme={{
            root: 'dropdown open',
            suggestions: 'dropdown-menu',
          }}
          onSuggestionSelected={(v, e) =>
            this.selectOption(v, e)}
          inputAttributes={{
            type: 'search',
            onChange: v => this.onInputChange(v),
          }}/>
        );
    }
}

WizardFilterMultiCollect.propTypes = {
  id: PropTypes.string.isRequired,
  addItem: PropTypes.func.isRequired,
  getHints: PropTypes.func.isRequired,
};


const WizardFilterCollectedItems = props =>
    <div> {
        props.items.map(item =>
          <Button
            key={item.key}
            bsSize="small"
            onClick={() => props.remove(item)}>
            <Glyphicon glyph="remove"/>
            {item.display}
          </Button>)
    }
    </div>;

WizardFilterCollectedItems.propTypes = {
  items: PropTypes.array.isRequired,
};
