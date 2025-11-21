import request from './request'

export function getClubMembers(params) {
  return request({
    url: '/api/club/members',  // 添加 /api 前缀
    method: 'get',
    params
  })
}

export function auditMember(memberId, status) {
  return request({
    url: '/api/member/audit',  // 添加 /api 前缀
    method: 'post',
    data: { member_id: memberId, audit_status: status }
  })
}

export function removeMember(memberId) {
  return request({
    url: '/api/member/remove',  // 添加 /api 前缀
    method: 'post',
    data: { member_id: memberId }
  })
}

export function joinClub(data) {
  return request({
    url: '/api/club/join',  // 添加 /api 前缀
    method: 'post',
    data
  })
}

export function getMyClubs(userId) {
  return request({
    url: `/api/user/${userId}/clubs`,  // 添加 /api 前缀
    method: 'get'
  })
}

// 退出社团
export function quitClub(data) {
  return request({
    url: '/api/member/quit',
    method: 'post',
    data
  })
}