var webpack = require('webpack');
var path = require('path');

module.exports = {
  entry: {
    reporting: './src/reporting/main',
    manageusers: './src/manageusers/main',
    nonuseroutreach: './src/nonuseroutreach/main',
    myprofile: './src/myprofile/main',
  },
  resolve: {
    root: path.resolve('src'),
    extensions: ['', '.js', '.jsx'],
  },
  output: {
    path: '../static/bundle',
    filename: '[name].js',
  },
  module: {
    loaders: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        query: {
          cacheDirectory: true,
        },
      },
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'eslint-loader',
      },
    ],
  },
  plugins: [
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
      minChunks: 2,
    }),
    // Dedupe slightly decreases output size.
    new webpack.optimize.DedupePlugin(),
    // Webpack docs recommend using this plugin.
    // It slightly decreasese output size.
    new webpack.optimize.OccurenceOrderPlugin(),
    // Minify.
    // Warnings are off as the output isn't useful in a log.
    // In development it can be useful to see this output to verify that
    // dead code removal is doing something sane.
    new webpack.optimize.UglifyJsPlugin({compress: {warnings: false}}),
  ],
};
