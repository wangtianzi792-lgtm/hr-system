import request from './request'

// 公司信息
export function getCompanyInfo() {
  return request({ url: '/settings/company', method: 'get' })
}

export function saveCompanyInfo(data) {
  return request({ url: '/settings/company', method: 'post', data })
}

// 考勤规则
export function getAttendanceRule() {
  return request({ url: '/settings/attendance-rule', method: 'get' })
}

export function saveAttendanceRule(data) {
  return request({ url: '/settings/attendance-rule', method: 'post', data })
}

// 假期设置
export function getLeaveRule() {
  return request({ url: '/settings/leave-rule', method: 'get' })
}

export function saveLeaveRule(data) {
  return request({ url: '/settings/leave-rule', method: 'post', data })
}

// 系统设置
export function getSystemConfig() {
  return request({ url: '/settings/system', method: 'get' })
}

export function saveSystemConfig(data) {
  return request({ url: '/settings/system', method: 'post', data })
}

// 操作日志
export function getLogs(params) {
  return request({ url: '/settings/logs', method: 'get', params })
}

export function createLog(data) {
  return request({ url: '/settings/logs', method: 'post', data })
}
