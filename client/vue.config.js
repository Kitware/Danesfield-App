module.exports = {
  devServer: {
    proxy: process.env.API_PROXY,
    public: "localhost:8080"
  },
  chainWebpack: config => {
    config.module
      .rule('js')
      .include
      .add('resonantgeo')

    config.module
      .rule('glsl')
      .test(/\.glsl$/)
      .include
      .add(/vtk\.js(\/|\\)/)
      .end()
      .use()
      .loader('shader-loader')
  }
}
