import React, {PropTypes} from 'react';
import {Link} from 'react-router';


export function LinkRow(props) {
  const {text, label, to} = props;
  return (
    <div className="row">
      <div className="col-xs-2" style={{textAlign: 'right'}}>
        <Link to={to}>{label}</Link>
      </div>
      <div className="col-xs-2 col-xs-offset-8">{text}</div>
    </div>
  );
}

LinkRow.propTypes = {
  text: PropTypes.string.isRequired,
  to: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
};
