import Vue from 'vue'
import App from './App.vue'
import router from './router'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import axios from 'axios'  // 添加这行

Vue.use(ElementUI)
Vue.config.productionTip = false

// 将axios挂载到Vue原型上，这样可以在组件中直接使用 this.$axios
Vue.prototype.$axios = axios

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')

Vue.prototype.$bus = new Vue()