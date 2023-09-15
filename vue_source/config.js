// config.js
const developmentConfig = {
    // 开发环境配置项
    apiBaseUrl: "http://192.168.207.129:8888",
  };
  
  const productionConfig = {
    // 生产环境配置项
    apiBaseUrl: "",
  };
  
  module.exports = process.env.NODE_ENV === 'production' ? productionConfig : developmentConfig;
  






