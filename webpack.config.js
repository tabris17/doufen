/* eslint strict: 0 */
'use strict';

const path = require('path');
const webpack = require('webpack');

module.exports ={
  target: 'electron-renderer',
  entry: {
      index: "./src/app/assets/js/index.js"
  },
  output: {
    path: path.join(__dirname, 'src', 'app', 'assets', 'js'),
    publicPath: path.join(__dirname, 'src', 'app'),
    filename: '[name].bundle.js',
  },
  module: {
    rules: [{
      test: /\.css$/,
      use: [ 'style-loader', 'css-loader' ]
    }]
  }
}