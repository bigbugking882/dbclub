import Vue from 'vue'
import VueRouter from 'vue-router'
import LogRes from '@/components/MyLogReg'
import User from '@/components/MyUser'
import Manage from '@/components/MyManage'

Vue.use(VueRouter)

export default new VueRouter({
  mode: 'history',
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      component: LogRes,
      meta: { title: "登录注册" }
    },
    {
      path: '/user',
      component: User,
      meta: { title: "社团系统-用户端" }
    },
    {
      path: '/manage',
      component: Manage,
      meta: { title: "社团系统-管理端" }
    }
  ]
})