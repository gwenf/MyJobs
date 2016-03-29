var prodConfig = require('./webpack.config.js');

prodConfig.plugins = [];

// Linux users not using docker can do without this.
prodConfig.watchOptions = {poll: 1000};

module.exports = prodConfig;
