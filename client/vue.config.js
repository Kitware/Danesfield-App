module.exports = {
  devServer: {
    proxy: process.env.API_PROXY
  },
  chainWebpack: config => {
    config.module
      .rule('js')
      .include
      .add('resonantgeo')
  }
}
