import request from './request'

// 获取Dashboard统计数据
export function getDashboardStats() {
  return request({
    url: '/dashboard/stats',
    method: 'get'
  })
}

// 获取今日考勤统计
export function getTodayStats() {
  return request({
    url: '/dashboard/today',
    method: 'get'
  })
}

// 获取本周趋势
export function getWeekTrend() {
  return request({
    url: '/dashboard/week-trend',
    method: 'get'
  })
}

// 获取部门统计
export function getDeptStats() {
  return request({
    url: '/dashboard/dept-stats',
    method: 'get'
  })
}

// 获取最近考勤记录
export function getRecentRecords(limit = 10) {
  return request({
    url: '/attendance/records',
    method: 'get',
    params: { limit }
  })
}
