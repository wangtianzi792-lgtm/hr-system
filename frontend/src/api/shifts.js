import request from './request'

// 班次列表
export function getShifts(params) {
  return request.get('/shifts/', { params })
}

// 创建班次
export function createShift(data) {
  return request.post('/shifts/', data)
}

// 更新班次
export function updateShift(id, data) {
  return request.put(`/shifts/${id}`, data)
}

// 删除班次
export function deleteShift(id) {
  return request.delete(`/shifts/${id}`)
}

// 分配班次给员工
export function assignShift(data) {
  return request.post('/shifts/assign', data)
}

// 获取员工班次分配
export function getEmployeeShifts(employeeId) {
  return request.get(`/shifts/employee/${employeeId}`)
}

// 排班表查询
export function getSchedules(params) {
  return request.get('/shifts/schedules', { params })
}

// 创建排班
export function createSchedule(data) {
  return request.post('/shifts/schedules', data)
}

// 批量排班
export function batchSchedule(data) {
  return request.post('/shifts/schedules/batch', data)
}

// 删除排班
export function deleteSchedule(id) {
  return request.delete(`/shifts/schedules/${id}`)
}
