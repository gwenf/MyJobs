var timer;

/**
 * A hodge podge of useful utility functions used across site. This is imported
 * in base.html before anything else to ensure that it is globally available.
 **/
var utils = {};

/**
 * Returns the value of the cookie. Returns null if that cookie is not found.
 * cookie: The name of the cookie to retreive.
 **/
utils.readCookie = function(cookie) {
    var nameEQ = cookie + '=';
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) === ' ') {
        c = c.substring(1, c.length);
      }
      if (c.indexOf(nameEQ) === 0) {
        return c.substring(nameEQ.length, c.length);
      }
    }
    return null;
  },

/**
 * Creates a new timer which redirects the user if the `loggedout` cookie is
 * set.
 *
 * url: The url to redirect to.
 **/
utils.logoutTimer = function(url) {
    if (!timer) {
      timer = window.setInterval(function() {
        // if we are logged out and not already on the home page
        if (this.readCookie('loggedout') && window.location.pathname !== url) {
          window.location.assign(url);
        }
      }, 500);
    } else {
      window.clearInterval(timer);
    }
  },
};
