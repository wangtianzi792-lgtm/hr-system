import request from './request'

// 部门列表
export function getDepartments(params) {
  return request.get('/departments/', { params })
}

// 部门树
export function getDepartmentTree() {
  return request.get('/departments/tree')
}

// 创建部门
export function createDepartment(data) {
  return request.post('/departments/', data)
}

// 更新部门
export function updateDepartment(id, data) {
  return request.put(`/departments/${id}`, data)
}

// 删除部门
export function deleteDepartment(id) {
  return request.delete(`/departments/${id}`)
}
