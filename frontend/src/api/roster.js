import request from './request'

export function getRosterList(params) {
  return request.get('/roster/', { params })
}

export function getRosterSummary() {
  return request.get('/roster/summary')
}

export function getRosterDepartments() {
  return request.get('/roster/departments')
}