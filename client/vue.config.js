module.exports = {
  publicPath: process.env.NODE_ENV === 'production'
    ? '/static/core3d/'
    : '/',
  chainWebpack: config => {
    // config.module
    //   .rule('js')
    //   .include
    //   .add('resonantgeo')

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
