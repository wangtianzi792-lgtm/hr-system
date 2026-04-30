import request from './request'

export function getOffboardingList(params) {
  return request.get('/offboarding/', { params })
}

export function createOffboarding(data) {
  return request.post('/offboarding/', data)
}

export function updateOffboarding(data) {
  return request.put(`/offboarding/${data.id}`, data)
}

export function deleteOffboarding(id) {
  return request.delete(`/offboarding/${id}`)
}

export function approveDept(id, data) {
  return request.post(`/offboarding/${id}/approve_dept`, data)
}

export function withdrawOffboarding(id, data) {
  return request.post(`/offboarding/${id}/withdraw`, data)
}

export function approveGm(id, data) {
  return request.post(`/offboarding/${id}/approve_gm`, data)
}

export function approveHr(id, data) {
  return request.post(`/offboarding/${id}/approve_hr`, data)
}
