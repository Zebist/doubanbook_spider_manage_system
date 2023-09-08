import axios from 'axios';

let config;
config = require('../../config.js');

const instance = axios.create({
  baseURL: config.apiBaseUrl, // 配置 baseURL
  timeout: 10000, // 请求超时时间，可根据需求修改
});

// 在请求发送前，可以添加一些请求拦截器的逻辑
instance.interceptors.request.use(
  config => {
    // 在请求发送前做一些处理
    return config;
  },
  error => {
    // 请求错误时做一些处理
    return Promise.reject(error);
  }
);

// 在收到响应后，可以添加一些响应拦截器的逻辑
instance.interceptors.response.use(
  response => {
    // 在响应收到后做一些处理
    return response;
  },
  error => {
    // 响应错误时做一些处理
    return Promise.reject(error);
  }
);

export default instance;