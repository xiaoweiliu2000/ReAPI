module.exports = {
  presets: [
    '@vue/cli-plugin-babel/preset'
  ],
  plugins: [
    ["prismjs", {
      "languages": ["javascript", "css", "markup", "python", "json"],
      "plugins": ["line-numbers"], //配置显示行号插件
      "theme": "tomorrow", // 主题
      "css": true
    }]
  ]
}
