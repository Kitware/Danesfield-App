module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: process.env.API_PROXY,
        secure: false
      },
      '/girder': {
        target: "http://localhost:8080",
        secure: false
      }
    },
    public: "localhost:8080"
  },
  baseUrl: process.env.NODE_ENV === 'production'
    ? '/static/core3d/'
    : '/',
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
