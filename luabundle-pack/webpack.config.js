const webpack = require("webpack");
const path = require('path');
module.exports = {
  entry: {
    main: './index.js'
  },
  output: {
    path: path.resolve(__dirname, "../src/tts"),
    filename: "luabundle.js",
    libraryTarget: "commonjs2",
  },
  devtool: false,
  resolve: {
    alias: {
      fs: path.resolve(__dirname, 'fs.js'),
      path: path.resolve(__dirname, 'path.js'),
    },
  },
  module: {
    rules: [
      {
	test:  path.resolve(__dirname, 'node_modules/luabundle/bundle/index.js'),
	use: {
	  loader: 'babel-loader',
	  options: {
	    plugins: ['babel-plugin-static-fs'],
	  },
	},
      },
    ],
  },
};
