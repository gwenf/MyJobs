import React, {PropTypes} from 'react';
import ClickOutHandler from 'react-onclickout';
import {isIE8} from 'common/dom';

export default function ClickOutCompat(props) {
  const {children, onClickOut} = props;

  if (!isIE8) {
    return (
      <ClickOutHandler onClickOut={(...args) => onClickOut(...args)}>
        {children}
      </ClickOutHandler>
    );
  }
  // ClickOutHandler does this. Do the same here so css selectors still work.
  return Array.isArray(children) ?
      <div>{children}</div> :
      React.Children.only(children);
}

ClickOutCompat.propTypes = {
  children: PropTypes.node.isRequired,
  onClickOut: PropTypes.func.isRequired,
};
