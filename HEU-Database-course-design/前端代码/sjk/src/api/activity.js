import request from './request'

export function getActivities(params) {
  return request({
    url: '/api/activities',  // 添加 /api 前缀
    method: 'get',
    params
  })
}

export function createActivity(data) {
  return request({
    url: '/api/activity/create',  // 添加 /api 前缀
    method: 'post',
    data
  })
}

export function updateActivity(data) {
  return request({
    url: '/api/activity/update',  // 添加 /api 前缀
    method: 'post',
    data
  })
}

export function deleteActivity(activityId) {
  return request({
    url: `/api/activity/delete/${activityId}`,  // 添加 /api 前缀
    method: 'delete'
  })
}

export function signupActivity(data) {
  return request({
    url: '/api/activity/signup',  // 添加 /api 前缀
    method: 'post',
    data
  })
}

// 获取我的活动
export function getMyActivities(userId) {
  return request({
    url: `/api/user/${userId}/activities`,
    method: 'get'
  })
}

// 取消活动报名
export function cancelActivitySignup(data) {
  return request({
    url: '/api/activity/cancel-signup',
    method: 'post',
    data
  })
}

export function auditActivity(data) {
  return request({
    url: '/api/activity/audit',
    method: 'post',
    data
  })
}