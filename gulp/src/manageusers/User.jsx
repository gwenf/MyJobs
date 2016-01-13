/* global $ */

import React from 'react';
import Button from 'react-bootstrap/lib/Button';
import {Link} from 'react-router';

import {validateEmail} from 'util/validateEmail';
import {getCsrf} from 'util/cookie';

import RolesMultiselect from './RolesMultiselect';
import HelpText from './HelpText';
import {ModalConfirm} from 'common/ui/ModalConfirm';

class User extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      apiResponseHelp: '',
      userEmail: '',
      userEmailHelp: '',
      roleMultiselectHelp: '',
      availableRoles: [],
      assignedRoles: [],
      api_response_message: '',
      confirmMessage: '',
    };
    // React components using ES6 no longer autobind 'this' to non React methods
    // Thank you: https://github.com/goatslacker/alt/issues/283
    this.onTextChange = this.onTextChange.bind(this);
    this.handleSaveUserClick = this.handleSaveUserClick.bind(this);
    this.handleDeleteUserClick = this.handleDeleteUserClick.bind(this);
  }
  componentDidMount() {
    const action = this.props.location.query.action;

    if (action === 'Edit') {
      $.get('/manage-users/api/users/' + this.props.params.userId, function getUser(results) {
        const userObject = results[this.props.params.userId];

        const userEmail = userObject.email;

        const availableRolesUnformatted = JSON.parse(userObject.roles.available);
        const availableRoles = availableRolesUnformatted.map( obj => {
          const role = {};
          role.id = obj.pk;
          role.name = obj.fields.name;
          return role;
        });

        const assignedRolesUnformatted = JSON.parse(userObject.roles.assigned);
        const assignedRoles = assignedRolesUnformatted.map( obj => {
          const role = {};
          role.id = obj.pk;
          role.name = obj.fields.name;
          return role;
        });

        this.setState({
          userEmail: userEmail,
          userEmailHelp: '',
          roleMultiselectHelp: '',
          apiResponseHelp: '',
          availableRoles: availableRoles,
          assignedRoles: assignedRoles,
        });
      }.bind(this));
    } else {
      $.get('/manage-users/api/roles/', function addUser(results) {
        const availableRoles = [];
        for (const roleId in results) {
          if (results.hasOwnProperty(roleId)) {
            availableRoles.push(
              {
                'id': roleId,
                'name': results[roleId].role.name,
              }
            );
          }
        }

        this.setState({
          userEmail: '',
          userEmailHelp: '',
          roleMultiselectHelp: '',
          apiResponseHelp: '',
          availableRoles: availableRoles,
          assignedRoles: [],
        });
      }.bind(this));
    }
  }
  onTextChange(event) {
    this.state.userEmail = event.target.value;

    const userEmail = this.state.userEmail;

    if (validateEmail(userEmail) === false) {
      this.setState({
        userEmail: this.state.userEmail,
        userEmailHelp: 'Invalid email',
        availableRoles: this.refs.roles.state.availableRoles,
        assignedRoles: this.refs.roles.state.assignedRoles,
      });
    } else {
      this.setState({
        userEmail: this.state.userEmail,
        userEmailHelp: '',
        api_response_message: '',
        availableRoles: this.refs.roles.state.availableRoles,
        assignedRoles: this.refs.roles.state.assignedRoles,
      });
    }
  }
  handleSaveUserClick() {
    // Grab form fields and validate
    // TODO: Warn user? If they remove a user from all roles, they will have to reinvite him.
    const userId = this.props.params.userId;

    let assignedRoles = this.refs.roles.state.assignedRoles;

    const userEmail = this.state.userEmail;

    if (validateEmail(userEmail) === false) {
      this.setState({
        userEmailHelp: 'Invalid email.',
        roleMultiselectHelp: '',
        availableRoles: this.refs.roles.state.availableRoles,
        assignedRoles: this.refs.roles.state.assignedRoles,
      });
      return;
    }

    if (assignedRoles.length < 1) {
      this.setState({
        userEmailHelp: '',
        roleMultiselectHelp: 'Each user must be assigned to at least one role.',
        availableRoles: this.refs.roles.state.availableRoles,
        assignedRoles: this.refs.roles.state.assignedRoles,
      });
      return;
    }

    // No errors? Clear help text
    this.setState({
      availableRoles: this.refs.roles.state.availableRoles,
      assignedRoles: this.refs.roles.state.assignedRoles,
    });

    // Format properly
    assignedRoles = assignedRoles.map( obj => {
      return obj.name;
    });

    // Determine URL based on action
    const action = this.props.location.query.action;

    let url = '';
    if ( action === 'Edit' ) {
      url = '/manage-users/api/users/edit/' + userId + '/';
    } else {
      url = '/manage-users/api/users/create/';
    }

    // Build data to send
    const dataToSend = {};
    dataToSend.csrfmiddlewaretoken = getCsrf();
    dataToSend.assigned_roles = assignedRoles;
    dataToSend.user_email = userEmail;

    // Submit to server
    $.post(url, dataToSend, function submitToServer(response) {
      if ( response.success === 'true' ) {
        // Reload API
        this.props.callUsersAPI();
        // Redirect user
        this.props.history.pushState(null, '/users');
      } else if ( response.success === 'false' ) {
        this.setState({
          apiResponseHelp: response.message,
          userEmail: this.state.userEmail,
          availableRoles: this.refs.roles.state.availableRoles,
          assignedRoles: this.refs.roles.state.assignedRoles,
        });
      }
    }.bind(this))
    .fail( function failGracefully(xhr) {
      if (xhr.status === 403) {
        this.setState({
          apiResponseHelp: 'Unable to save user. Insufficient privileges.',
        });
      }
    }.bind(this));
  }
  handleDeleteUserClick() {
    this.setState({
      confirmMessage: 'Are you sure you want to delete this user?',
    });
  }
  handleRejectedDeleteUser() {
    this.setState({
      confirmMessage: '',
    });
  }
  handleConfirmedDeleteUser() {
    const history = this.props.history;
    // Temporary until I replace $.ajax jQuery with vanilla JS ES6 arrow function
    const self = this;

    this.setState({
      confirmMessage: '',
    });

    const userId = this.props.params.userId;

    const csrf = getCsrf();

    // Submit to server
    $.ajax( '/manage-users/api/users/delete/' + userId + '/', {
      type: 'DELETE',
      beforeSend: function beforeSend(xhr) {
        xhr.setRequestHeader('X-CSRFToken', csrf);
      },
      success: function success() {
        // Reload API
        self.props.callUsersAPI();
        // Redirect user
        history.pushState(null, '/users');
      }})
      .fail( function failGracefully(xhr) {
        if (xhr.status === 403) {
          this.setState({
            apiResponseHelp: 'User not deleted. Insufficient privileges.',
          });
        }
      }.bind(this));
  }
  renderConfirm() {
    const {confirmMessage} = this.state;
    return (
      <ModalConfirm
        show={Boolean(confirmMessage)}
        title="Confirmation Required"
        message={confirmMessage}
        onConfirm={() => this.handleConfirmedDeleteUser()}
        onReject={() => this.handleRejectedDeleteUser()}/>
    );
  }
  render() {
    let deleteUserButton = '';

    let userEmailInput = '';

    const action = this.props.location.query.action;

    if (action === 'Edit') {
      userEmailInput = <input id="id_userEmail" maxLength="255" name="id_userEmail" type="email" readOnly value={this.state.userEmail} size="35"/>;
      deleteUserButton = <Button className="pull-right" onClick={this.handleDeleteUserClick}>Delete User</Button>;
    } else {
      userEmailInput = <input id="id_userEmail" maxLength="255" name="id_userEmail" type="email" value={this.state.userEmail} onChange={this.onTextChange} size="35"/>;
    }

    const userEmailHelp = this.state.userEmailHelp;
    const roleMultiselectHelp = this.state.roleMultiselectHelp;
    const apiResponseHelp = this.state.apiResponseHelp;

    return (
      <div>
        {this.renderConfirm()}
        <div className="row">
          <div className="col-xs-12">
            <div className="wrapper-header">
              <h2>{action} User</h2>
            </div>
            <div className="product-card-full no-highlight">

              <div className="row">
                <div className="col-xs-12">
                  <HelpText message={userEmailHelp} />
                  <label htmlFor="id_userEmail">User Email*:</label>
                  {userEmailInput}
                </div>
              </div>

              <div className="row">
                <div className="col-xs-12">
                  <hr/>
                  <HelpText message={roleMultiselectHelp} />
                  <RolesMultiselect availableRoles={this.state.availableRoles} assignedRoles={this.state.assignedRoles} ref="roles"/>
                  <span id="role_select_help" className="help-text">To select multiple options on Windows, hold down the Ctrl key. On OS X, hold down the Command key.</span>
                  <hr />
                </div>
              </div>

              <div className="row">
                <div className="col-xs-12">
                  <span className="primary pull-right">
                    <HelpText message={apiResponseHelp} />
                  </span>
                </div>

                <div className="col-xs-12">
                  <Button className="primary pull-right" onClick={this.handleSaveUserClick}>Save User</Button>
                  {deleteUserButton}
                  <Link to="users" className="pull-right btn btn-default">Cancel</Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

User.propTypes = {
  location: React.PropTypes.object.isRequired,
  params: React.PropTypes.object.isRequired,
  callUsersAPI: React.PropTypes.func,
  history: React.PropTypes.object.isRequired,
};

export default User;
