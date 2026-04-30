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

export function getRosterPositions() {
  return request.get('/roster/positions')
}

export function lookupRoster(q) {
  return request.get('/roster/lookup', { params: { q } })
}