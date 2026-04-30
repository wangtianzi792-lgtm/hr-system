import request from './request'

// 设备列表
// check_status=true 实时检测所有设备状态
export function getDevices(params, checkStatus = false) {
  return request.get('/devices/', { params: { ...params, check_status: checkStatus } })
}

// 创建设备
export function createDevice(data) {
  return request.post('/devices/', data)
}

// 更新设备
export function updateDevice(id, data) {
  return request.put(`/devices/${id}`, data)
}

// 删除设备
export function deleteDevice(id) {
  return request.delete(`/devices/${id}`)
}

// 检测设备状态
export function checkDeviceStatus(id) {
  return request.get(`/devices/${id}/status`)
}

// 同步考勤机数据
export function syncDevice(id) {
  return request.post(`/devices/${id}/sync`)
}

// 重启设备
export function restartDevice(id) {
  return request.post(`/devices/${id}/restart`)
}

// 下载打卡记录
export function downloadRecords(id) {
  return request.post(`/devices/${id}/download-records`)
}
