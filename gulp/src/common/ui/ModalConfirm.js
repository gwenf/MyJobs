import React, {Component, PropTypes} from 'react';


export class ModalConfirm extends Component {
  onYesClick() {
    const {onConfirm} = this.props;
    onConfirm();
  }

  onNoClick() {
    const {onReject} = this.props;
    onReject();
  }

  onCloseClick() {
    const {onReject} = this.props;
    onReject();
  }

  onBackdropClick() {
    const {onReject} = this.props;
    onReject();
  }

  render() {
    const {title, message, show} = this.props;
    const display = show ? 'block' : 'none';
    return (
      <div>
        <div className="modal-backdrop" style={{
          display,
          opacity: '0.3',
        }}>
        </div>
        <div className="modal" role="dialog" style={{
          display,
        }}
          onClick={e => this.onBackdropClick(e)}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <button
                  type="button"
                  className="close"
                  aria-label="Close"
                  onClick={e => this.onCloseClick(e)}>
                  <span aria-hidden="true">&times;</span>
                </button>
                <h4 className="modal-title">{title}</h4>
              </div>
              <div className="modal-body">
                {message}
              </div>
              <div className="modal-footer">
                <button
                  className="btn btn-default"
                  onClick={e => this.onNoClick(e)}>
                  No
                </button>
                <button
                  className="btn btn-default"
                  onClick={e => this.onYesClick(e)}>
                  Yes
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}


ModalConfirm.propTypes = {
  title: PropTypes.string.isRequired,
  message: PropTypes.string.isRequired,
  show: PropTypes.bool.isRequired,
  onConfirm: PropTypes.func.isRequired,
  onReject: PropTypes.func.isRequired,
};
