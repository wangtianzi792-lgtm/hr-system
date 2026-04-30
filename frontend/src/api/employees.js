import request from './request'

// 员工列表
export function getEmployees(params) {
  return request.get('/employees/', { params })
}

// 创建员工
export function createEmployee(data) {
  return request.post('/employees/', data)
}

// 更新员工
export function updateEmployee(id, data) {
  return request.put(`/employees/${id}`, data)
}

// 删除员工
export function deleteEmployee(id) {
  return request.delete(`/employees/${id}`)
}

// 下发员工到考勤机
export function deployToDevice(employeeId, deviceId) {
  return request.post(`/employees/${employeeId}/enroll`, { device_id: deviceId })
}

// 从考勤机移除员工
export function removeFromDevice(employeeId, deviceId) {
  return request.post(`/employees/${employeeId}/remove-from-device`, { device_id: deviceId })
}

// 导出员工
export function exportEmployees(params) {
  return request.get('/employees/export', { params, responseType: 'blob' })
}
