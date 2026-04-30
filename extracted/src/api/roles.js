import request from './request'

// 角色列表
export function getRoles(params) {
  return request.get('/roles', { params })
}

// 创建角色
export function createRole(data) {
  return request.post('/roles', data)
}

// 更新角色
export function updateRole(id, data) {
  return request.put(`/roles/${id}`, data)
}

// 删除角色
export function deleteRole(id) {
  return request.delete(`/roles/${id}`)
}

// 获取所有权限列表
export function getPermissions() {
  return request.get('/roles/permissions')
}

// 获取角色的权限列表
export function getRolePermissions(roleId) {
  return request.get(`/roles/${roleId}/permissions`)
}
