export function getToken() {
  return localStorage.getItem('token')
}

export function setToken(token) {
  localStorage.setItem('token', token)
}

export function removeToken() {
  localStorage.removeItem('token')
}

export function getUserInfo() {
  const user = localStorage.getItem('user')
  return user ? JSON.parse(user) : null
}

export function setUserInfo(user) {
  localStorage.setItem('user', JSON.stringify(user))
}

export function removeUserInfo() {
  localStorage.removeItem('user')
}

export function isAdmin() {
  const user = getUserInfo()
  return user && user.role === 2
}

export function isClubAdmin() {
  const user = getUserInfo()
  return user && user.role === 1
}