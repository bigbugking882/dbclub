import request from './request'

export function getClubs() {
  return request({
    url: '/api/clubs',  // 添加 /api 前缀
    method: 'get'
  })
}

export function createClub(data) {
  return request({
    url: '/api/club/create',  // 添加 /api 前缀
    method: 'post',
    data
  })
}

export function updateClub(data) {
  return request({
    url: '/api/club/update',  // 添加 /api 前缀
    method: 'post',
    data
  })
}