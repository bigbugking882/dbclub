import Vue from 'vue'
import Router from 'vue-router'
import Login from '@/views/Login'
import Register from '@/views/Register'
import UserHome from '@/views/UserHome'
import AdminHome from '@/views/AdminHome'

Vue.use(Router)

export default new Router({
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/user', component: UserHome },
    { path: '/admin', component: AdminHome }
  ]
})