const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    https: false,
    port: 8082,
    proxy: {
      "/admin/api": {
        target: "http://127.0.0.1:8081/",
        // target: "https://admin.your-club.com/",
        ws: true,
        changeOrigin: true
      }
    }
  }
})

