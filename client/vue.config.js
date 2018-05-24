module.exports = {
    devServer: {
        proxy: 'http://localhost:8081'
    },
    chainWebpack: config => {
        config.module
            .rule('js')
            .include
            .add('resonantgeo')
    }
}
