import Vue from 'vue'
import App from './App.vue'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import VXETable from 'vxe-table'
import 'vxe-table/lib/style.css'
import axios from './js/axios'; // 导入创建的 Axios 插件

Vue.prototype.$axios = axios; // 将 Axios 实例添加到 Vue 原型上


Vue.config.productionTip = false

Vue.use(VXETable)
Vue.use(ElementUI);
new Vue({
  render: h => h(App),
  axios: axios,
}).$mount('#app')
