const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: 'warning',
  devServer: {
    // 代理解决跨域
    // host: 'localhost',
    port: 8080,
    //这里的ip和端口是前端项目的;下面为需要跨域访问后端项目
    proxy: {
      '/backend': {
          target: 'http://localhost:8081/',//这里填入你要请求的接口的前缀
          ws:true,//代理websocked
          changeOrigin:true, //虚拟的站点需要更管origin
          secure: false, //是否https接口
          pathRewrite:{
            '^/backend':''//重写路径
        },
        headers: {
          referer: 'http://localhost:8080/backend/', //这里后端做了拒绝策略限制，请求头必须携带referer，否则无法访问后台
        }
      },
      '/rec': {
        target: 'http://localhost:9000/',//这里填入你要请求的接口的前缀
        ws:true,//代理websocked
        changeOrigin:true, //虚拟的站点需要更管origin
        secure: false, //是否https接口
        pathRewrite:{
          '^/rec':''//重写路径
        },
        headers: {
          referer: 'http://localhost:8080/rec/', //这里后端做了拒绝策略限制，请求头必须携带referer，否则无法访问后台
        }
      },
      
    }
  }
})
