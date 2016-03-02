require('babel/register');
require('babel/polyfill');

var fs = require('fs');
var path = require('path');
var gulp = require('gulp');
var webpack = require('webpack');
var util = require('gulp-util');
var gulpif = require('gulp-if');
var jasmine = require('gulp-jasmine');
var eslint = require('gulp-eslint');


// This build produces several javascript bundles.
// * vendor.js - Contains all the libraries we use, bundled and minified.
//     This code is shared by all other app bundles. It is expected to be
//     larger than app bundles and shared by all pages needing this
//     infrastructure.
//
//     In production this bundle also contains whatever code webpack deemed
//     as common to all app bundles.
//
// * reporting.js, [other-apps].js, etc. - These contain mostly only code
//     used in a specific application. There should be one for each "app"
//     in our site.
//
// For production builds use the default target.
//
// For development run the default target, then leave the watch target running.

// These go in vendor.js and are left out of app specific bundles.
var vendorLibs = [
  'react',
  'react-dom',
  // Importing all of react-bootstrap _really_ bloats the bundle.
  // Just pull what we use.
  'react-bootstrap/lib/Button.js',
  'react-bootstrap/lib/Accordion.js',
  'react-bootstrap/lib/Panel.js',
  'react-bootstrap/lib/Glyphicon.js',
  'react-autosuggest',
  'fetch-polyfill',
  'es6-promise',
  'warning',
];

var dest = '../static/bundle';

var strip_debug = true;

function webpackConfig() {
  return {
    entry: {
      reporting: './src/reporting/main',
      manageusers: './src/manageusers/main',
      nonuseroutreach: './src/nonuseroutreach/main',
      vendor: vendorLibs,
    },
    resolve: {
      root: path.resolve('src'),
      // you can now require('file') instead of require('file.coffee')
      extensions: ['', '.js', '.jsx'],
      // Thank you internet man! http://stackoverflow.com/a/32444088
      alias: {
        'react': path.join(__dirname, 'node_modules', 'react'),
      },
    },
    output: {
      path: '../static/bundle',
      filename: '[name].js',
    },
    module: {
      loaders: [
        {
          test: /\.js$/,
          exclude: /node_modules/,
          loader: "babel-loader",
          query: {
            cacheDirectory: true,
          },
        },
        {
          test: /\.jsx$/,
          exclude: /node_modules/,
          loader: "babel-loader",
          query: {
            cacheDirectory: true,
          },
        },
      ],
    },
    plugins: [],
  };
}

gulp.task('bundle', function(callback) {
  var config = webpackConfig();
  config.plugins.push(
    // React is smaller, faster, and silent in this mode.
    // The warning module is also silent in this mode.
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': '"production"',
    }),
    // Factor common code in to vendor.js.
    // This also establishes the parent relationship between the vendor
    // and app chunks.
    new webpack.optimize.CommonsChunkPlugin({
      name: 'vendor',
      filename: 'vendor.js',
    }),
    // No idea if Dedupe and OccurenceOrder are actually doing anything.
    new webpack.optimize.DedupePlugin(),
    new webpack.optimize.OccurenceOrderPlugin(),
    // Minify.
    // Warnings are off as the output isn't useful in a log.
    // In development it can be useful to see this output to verify that
    // dead code removal is doing something sane.
    new webpack.optimize.UglifyJsPlugin({
      compress: {
        warnings: false,
      },
    }));
  webpack(config, function(err, stats) {
    if(err) {
      throw new util.PluginError("webpack", err);
    }
    util.log(stats.toString("minimal"));
    if (stats.hasErrors()) {
      callback('webpack error');
      return;
    }
    fs.writeFile('profile.json', JSON.stringify(stats.toJson(), null, 4));
    callback();
  });
});

// Object to use for webpack's in memory cache. This seems to be the only
// way to have an incremental build with webpack.
var webpackCache = {};

gulp.task('dev-bundle', function(callback) {
  // This bundle is tuned for build speed and development convenience.
  var config = webpackConfig();
  config.debug = true;
  config.devtool = 'eval-cheap-module-source-map';
  config.cache = webpackCache;
  config.resolve.unsafeCache = true;
  config.profile = true;
  config.plugins.push(
    // Still generate a vendor.js but don't bother factoring any common
    // app code into it.
    new webpack.optimize.CommonsChunkPlugin({
      name: 'vendor',
      filename: 'vendor.js',
      minChunks: Infinity,
    }))
  webpack(config, function(err, stats) {
    if(err) {
      throw new util.PluginError("webpack", err);
    }
    util.log(stats.toString('minimal'));
    if (stats.hasErrors()) {
      callback('webpack error');
      return;
    }
    fs.writeFile('profile.json', JSON.stringify(stats.toJson(), null, 4));
    callback();
  });
});

gulp.task('test', function() {
  return gulp.src(['./src/**/spec/*.js'])
    .pipe(jasmine({
      includeStackTrace: false,
    }));
});

function lintOptions() {
  return {
    extends: 'airbnb',
    env: {
      jasmine: true,
    },
    parser: 'babel-eslint',
    plugins: ['babel'],
    rules: {
      "babel/object-curly-spacing": 1,
      "babel/no-await-in-loop": 2,
      // this allows use of confirm, which is currently acceptable
      "no-alert": 0,
    },
  };
}

/**
 * lint-fix: run eslint with fix mode on.
 *
 * This can be helpful in limited circumstances. Be careful.
 *
 * It is not part of watch or the default build. Let's keep it
 * that way.
 */
gulp.task('lint-fix', function() {
  function isFixed(file) {
    return file.eslint != null && file.eslint.fixed;
  };
  var lintOpts = lintOptions();
  lintOpts.fix = true;
  return gulp.src(['./src/somedir/**/*js'])
    .pipe(eslint(lintOpts))
    .pipe(eslint.format())
    .pipe(gulpif(isFixed, gulp.dest("./src")));
});

gulp.task('lint', function() {
  return gulp.src(['./src/**/*.js', './src/**/*.jsx'])
    .pipe(eslint(lintOptions()))
    .pipe(eslint.format());
});

// Build everything. Good way to start after a git checkout.
gulp.task('build', ['bundle', 'lint', 'test']);

gulp.task('watch-tasks', ['dev-bundle', 'test', 'lint']);

// Leave this running in development for a pleasant experience.
gulp.task('watch', function() {
    return gulp.watch('src/**/*', ['watch-tasks']);
});

// This is how we build in production.
// In production NODE_ENV is set to 'production'.
gulp.task('default', ['build']);
