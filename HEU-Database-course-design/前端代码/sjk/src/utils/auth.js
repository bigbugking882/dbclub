export function getToken() {
  return sessionStorage.getItem('token')
}

export function setToken(token) {
  sessionStorage.setItem('token', token)
}

export function removeToken() {
  sessionStorage.removeItem('token')
}

export function getUserInfo() {
  const user = sessionStorage.getItem('user')
  return user ? JSON.parse(user) : null
}

export function setUserInfo(user) {
  sessionStorage.setItem('user', JSON.stringify(user))
}

export function removeUserInfo() {
  sessionStorage.removeItem('user')
}

export function isAdmin() {
  const user = getUserInfo()
  return user && user.role === 2
}

export function isClubAdmin() {
  const user = getUserInfo()
  return user && user.role === 1
}