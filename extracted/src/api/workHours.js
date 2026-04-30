import request from './request'

export function getDepartmentBreaks() {
  return request.get('/department-breaks/')
}

export function saveDepartmentBreak(data) {
  return request.post('/department-breaks/', data)
}

export function updateDepartmentBreak(departmentId, data) {
  return request.put(`/department-breaks/${departmentId}`, data)
}

export function deleteDepartmentBreak(departmentId) {
  return request.delete(`/department-breaks/${departmentId}`)
}
