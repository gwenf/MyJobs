import React, {PropTypes} from 'react';
import Button from 'react-bootstrap/lib/Button';
import Glyphicon from 'react-bootstrap/lib/Glyphicon';


// Future: factor out components likely to be useful and move them to a
// module suitable for sharing between apps.

export function WizardFilterCollectedItems(props) {
  return (
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
    </div>
  );
}

WizardFilterCollectedItems.propTypes = {
  items: PropTypes.array.isRequired,
};
