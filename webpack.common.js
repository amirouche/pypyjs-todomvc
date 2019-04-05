// https://webpack.js.org/guides/author-libraries/
const config = {
    entry: ['./index.js'],
    output: {
        path: __dirname,
        filename: 'helpers.js',
        library: 'helpers',
        libraryTarget:'var',
    },
    module: {
        loaders: [
            {
                loader:'babel-loader',
                test: /\.js$/,
                exclude:  /node_modules/,
                query: {
                    presets: ['es2015']
                }
            }
        ]
    },
    resolve: {
        extensions: ['.js']
    }
}
module.exports = config;
