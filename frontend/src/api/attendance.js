import request from './request'

// 考勤记录列表（从原始打卡记录）
export function getAttendanceRecords(params) {
  return request.get('/attendance/punch-records', { params })
}

// 采集考勤数据
export function collectAttendance(deviceId) {
  return request.post('/attendance/collect', deviceId ? { device_id: deviceId } : {})
}

// 考勤报表
export function getAttendanceReport(params) {
  return request.get('/attendance/report', { params })
}

// 考勤统计
export function getAttendanceStatistics(params) {
  return request.get('/attendance/statistics', { params })
}

// 导出考勤
export function exportAttendance(params) {
  return request.get('/attendance/export', { params })
}

// 今日考勤概况
export function getTodaySummary() {
  return request.get('/attendance/summary/today')
}

// ============ 班次管理 ============

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

// ============ 排班管理 ============

// 排班列表
export function getSchedules(params) {
  return request.get('/schedules/', { params })
}

// 创建/更新排班
export function createSchedule(data) {
  return request.post('/schedules/', data)
}

// 删除排班
export function deleteSchedule(id) {
  return request.delete(`/schedules/${id}`)
}

// 批量排班（按部门/日期）
export function batchSchedule(data) {
  return request.post('/schedules/batch', data)
}

// ============ 请假管理 ============

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
export function approveLeaveRequest(id, data) {
  return request.post(`/leave/${id}/approve`, data)
}

// ============ 加班管理 ============

// 加班列表
export function getOvertimeRequests(params) {
  return request.get('/overtime/', { params })
}

// 创建加班
export function createOvertimeRequest(data) {
  return request.post('/overtime/', data)
}

// 审批加班
export function approveOvertimeRequest(id, data) {
  return request.post(`/overtime/${id}/approve`, data)
}

// ============ 考勤规则 ============

// 获取考勤规则
export function getAttendanceRules() {
  return request.get('/attendance/rules')
}

// 更新考勤规则
export function updateAttendanceRules(data) {
  return request.put('/attendance/rules', data)
}

// 获取假期余额
export function getLeaveBalance(employeeId) {
  return request.get(`/leave/balance/${employeeId}`)
}