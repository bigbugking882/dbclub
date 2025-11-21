import axios from 'axios'
import { Message } from 'element-ui'
import { getToken } from '@/utils/auth'

// 创建axios实例
const service = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 在请求头中添加token
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token
    }
    return config
  },
  error => {
    console.log('Request Error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // 如果返回的状态码不是200，则判断为错误
    if (res.status !== 200) {
      Message.error(res.message || 'Error')
      return Promise.reject(new Error(res.message || 'Error'))
    }
    
    return res
  },
  error => {
    console.log('Response Error:', error)
    
    if (error.response) {
      switch (error.response.status) {
        case 401:
          Message.error('未授权，请重新登录')
          // 清除token并跳转到登录页
          localStorage.removeItem('user')
          localStorage.removeItem('token')
          window.location.href = '/login'
          break
        case 403:
          Message.error('拒绝访问')
          break
        case 404:
          Message.error('请求的资源不存在')
          break
        case 500:
          Message.error('服务器内部错误')
          break
        default:
          Message.error('网络错误')
      }
    } else {
      Message.error('网络连接失败')
    }
    
    return Promise.reject(error)
  }
)

export default service