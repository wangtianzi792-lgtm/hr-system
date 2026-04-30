import axios from 'axios'
import { getEmployees as empApi, getDepartments as deptApi } from './employees'
import { getEmployees } from './employees'
import { getDepartments } from './departments'

const api = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// ==================== 考核周期管理 ====================

// 获取考核周期列表
export function getCycles(params) {
  return api.get('/api/evaluation/cycles', { params })
}

// 获取考核周期详情（含维度）
export function getCycleDetail(cycleId) {
  return api.get(`/api/evaluation/cycles/${cycleId}`)
}

// 创建考核周期
export function createCycle(data) {
  return api.post('/api/evaluation/cycles', data)
}

// 更新考核周期
export function updateCycle(cycleId, data) {
  return api.put(`/api/evaluation/cycles/${cycleId}`, data)
}

// 更新考核周期状态
export function updateCycleStatus(cycleId, status) {
  return api.put(`/api/evaluation/cycles/${cycleId}/status?status=${status}`)
}

// 删除考核周期
export function deleteCycle(cycleId) {
  return api.delete(`/api/evaluation/cycles/${cycleId}`)
}

// ==================== 考核评价管理 ====================

// 获取考核评价列表
export function getEvaluations(params) {
  return api.get('/api/evaluation/evaluations', { params })
}

// 提交考核评价
export function submitEvaluation(data) {
  return api.post('/api/evaluation/evaluations', data)
}

// 获取我的考核任务
export function getMyTasks(reviewerId, cycleId) {
  return api.get('/api/evaluation/my-tasks', { params: { reviewer_id: reviewerId, cycle_id: cycleId } })
}

// ==================== 360考核报告 ====================

// 获取考核周期汇总报告
export function getCycleReports(cycleId) {
  return api.get(`/api/evaluation/reports/${cycleId}`)
}

// 生成考核汇总报告
export function generateReports(cycleId) {
  return api.post(`/api/evaluation/generate-reports/${cycleId}`)
}

// 获取考核周期统计数据
export function getCycleStats(cycleId) {
  return api.get(`/api/evaluation/stats/${cycleId}`)
}

export default {
  getCycles,
  getCycleDetail,
  createCycle,
  updateCycle,
  updateCycleStatus,
  deleteCycle,
  getEvaluations,
  submitEvaluation,
  getMyTasks,
  getCycleReports,
  generateReports,
  getCycleStats,
  getEmployees,
  getDepartments
}
