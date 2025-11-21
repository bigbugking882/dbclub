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

// 获取社团成员列表
export function getClubMembers(params) {
  return request({
    url: '/api/club/members',
    method: 'get',
    params
  })
}

// 获取社团活动列表
export function getClubActivities(params) {
  return request({
    url: '/api/club/activities',
    method: 'get',
    params
  })
}

// 移除社团成员
export function removeClubMember(memberId) {
  return request({
    url: `/api/club/member/${memberId}`,
    method: 'delete'
  })
}

// 删除活动
export function deleteActivity(activityId) {
  return request({
    url: `/api/activity/${activityId}`,
    method: 'delete'
  })
}

export function deleteClub(clubId) {
  return request({
    url: `/api/club/delete/${clubId}`,
    method: 'delete'
  })
}