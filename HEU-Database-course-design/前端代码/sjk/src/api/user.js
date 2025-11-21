import request from './request'

export function userLogin(data) {
  return request({
    url: '/api/user/login',  // 添加 /api 前缀
    method: 'post',
    data
  })
}

export function userRegister(data) {
  return request({
    url: '/api/user/register',  // 添加 /api 前缀
    method: 'post',
    data
  })
}

export function getUsers() {
  return request({
    url: '/api/users',  // 添加 /api 前缀
    method: 'get'
  })
}

export function updateUser(data) {
  return request({
    url: '/api/user/update',  // 添加 /api 前缀
    method: 'post',
    data
  })
}