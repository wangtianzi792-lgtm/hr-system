import request from './request'

// 请假列表
export function getLeaveRequests(params) {
  return request.get('/leave/', { params })
}

// 创建请假
export function createLeaveRequest(data) {
  return request.post('/leave/', data)
}

// 更新请假
export function updateLeaveRequest(id, data) {
  return request.put(`/leave/${id}`, data)
}

// 删除请假
export function deleteLeaveRequest(id) {
  return request.delete(`/leave/${id}`)
}

// 审批请假
export function approveLeaveRequest(id, approved, comment) {
  return request.post(`/leave/${id}/approve?approved=${approved}&comment=${comment || ''}`)
}

// 加班列表
export function getOvertimeRequests(params) {
  return request.get('/leave/overtime', { params })
}

// 创建加班
export function createOvertimeRequest(data) {
  return request.post('/leave/overtime', data)
}

// 审批加班
export function approveOvertimeRequest(id, approved, comment) {
  return request.post(`/leave/overtime/${id}/approve?approved=${approved}&comment=${comment || ''}`)
}

// 考勤规则
export function getAttendanceRules() {
  return request.get('/leave/rules')
}

// 更新考勤规则
export function updateAttendanceRules(data) {
  return request.put('/leave/rules', data)
}

// 假期余额
export function getLeaveBalance(employeeId, year) {
  return request.get(`/leave/balance/${employeeId}?year=${year || new Date().getFullYear()}`)
}
