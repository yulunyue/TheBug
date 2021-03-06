const path = require('path') // 处理绝对路径
module.exports = {
    entry: path.join(__dirname, 'src/index.js'), // 入口文件
    output: {
        path: path.join(__dirname, './dist'), //打包后的文件存放的地方
        filename: 'main.js' //打包后输出文件的文件名
    },
    mode: "production",
    devServer: {
        contentBase: "./",
        port: "8888",
        inline: true,
        historyApiFallback: true,
        hot: true
    }
}