const path = require('path');

let config = {
    entry: './app.js',
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, '../static/js/_build_/')
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader"
                }
            }, {
                test: /\.(css)$/,
                exclude: /node_modules/,
                loader: ["style-loader", "css-loader?sourceMap"]
            }, {
                test: /\.(scss)$/,
                loader: ["style-loader", "css-loader?sourceMap", "sass-loader"]
            }, {
                test: /\.(png|jpg|jpeg|gif|woff|woff2)$/,
                loader: 'url-loader?limit=8192'
            }
        ]
    },
    resolve: {
        extensions: ['.js', '.jsx'],
        alias: {
            constants$: path.resolve(__dirname, '../constants.json')
        },
        modules: [
            path.resolve(__dirname),
            'node_modules',
        ]
    }
}

module.exports = (env, argv) => {
    console.log(argv.mode);
    return config;
};
