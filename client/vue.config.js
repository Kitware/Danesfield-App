module.exports = {
  devServer: {
    proxy: process.env.API_PROXY
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
