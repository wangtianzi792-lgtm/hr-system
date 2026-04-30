<template>
  <div class="page-container">
    <!-- 搜索和操作栏 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="24" style="text-align: right;">
          <el-button type="primary" @click="showAddDialog" style="background-color: #ec6921; border-color: #ec6921;">
            <el-icon><Plus /></el-icon>新增角色
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 角色列表 -->
    <el-card style="margin-top: 20px;">
      <el-table :data="roleList" v-loading="loading" style="width: 100%" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="display_name" label="角色名称" min-width="150" />
        <el-table-column prop="name" label="角色标识" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="is_system" label="系统角色" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.is_system ? 'success' : 'info'" size="small">
              {{ scope.row.is_system ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="权限数量" width="120">
          <template #default="scope">
            <el-tag type="warning" size="small">{{ scope.row.permissions?.length || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link size="small" @click="showEditDialog(scope.row)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(scope.row)" :disabled="scope.row.is_system">
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="角色标识" prop="name">
          <el-input v-model="form.name" placeholder="如: hr_manager" :disabled="isEdit" maxlength="50" />
        </el-form-item>
        <el-form-item label="角色名称" prop="display_name">
          <el-input v-model="form.display_name" placeholder="如: 人事经理" maxlength="100" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="角色描述" maxlength="500" show-word-limit />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" :max="9999" />
        </el-form-item>
        <el-form-item label="权限分配" prop="permissions">
          <div class="permission-groups">
            <div v-for="group in permissionGroups" :key="group.category" class="permission-group">
              <div class="group-title">
                <el-checkbox
                  :indeterminate="group.indeterminate"
                  v-model="group.checkAll"
                  @change="handleCheckAllChange(group)"
                >
                  {{ group.category }}
                </el-checkbox>
              </div>
              <el-checkbox-group v-model="form.permission_ids">
                <el-checkbox
                  v-for="perm in group.permissions"
                  :key="perm.id"
                  :label="perm.id"
                  :disabled="form.is_system"
                >
                  {{ perm.display_name }}
                </el-checkbox>
              </el-checkbox-group>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 删除确认 -->
    <el-dialog v-model="deleteDialogVisible" title="确认删除" width="400px">
      <p>确定要删除角色 <strong>{{ currentRole?.display_name }}</strong> 吗？</p>
      <p style="color: #e6a23c; font-size: 13px; margin-top: 10px;">
        <el-icon><Warning /></el-icon> 删除后无法恢复，请谨慎操作
      </p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmDelete" :loading="deleting">删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getRoles, createRole, updateRole, deleteRole, getPermissions } from '@/api/roles'

const loading = ref(false)
const submitting = ref(false)
const deleting = ref(false)
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const formRef = ref(null)
const dialogTitle = ref('')
const isEdit = ref(false)
const currentRole = ref(null)
const roleList = ref([])
const allPermissions = ref([])

const defaultForm = {
  name: '',
  display_name: '',
  description: '',
  sort_order: 0,
  is_system: false,
  permission_ids: []
}

const form = reactive({ ...defaultForm })

const rules = {
  name: [{ required: true, message: '请输入角色标识', trigger: 'blur' }],
  display_name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }]
}

// 按分类分组的权限
const permissionGroups = computed(() => {
  const categories = {}
  allPermissions.value.forEach(p => {
    if (!categories[p.category]) {
      categories[p.category] = { category: p.category, permissions: [], checkAll: false, indeterminate: false }
    }
    categories[p.category].permissions.push(p)
  })
  
  // 检查全选状态
  Object.values(categories).forEach(group => {
    const checked = form.permission_ids.filter(id => group.permissions.some(p => p.id === id)).length
    group.checkAll = checked === group.permissions.length && group.permissions.length > 0
    group.indeterminate = checked > 0 && checked < group.permissions.length
  })
  
  return Object.values(categories)
})

// 全选/取消全选
function handleCheckAllChange(group) {
  if (group.checkAll) {
    form.permission_ids = [...new Set([...form.permission_ids, ...group.permissions.map(p => p.id)])]
  } else {
    form.permission_ids = form.permission_ids.filter(id => !group.permissions.some(p => p.id === id))
  }
}

// 加载角色列表
async function loadRoles() {
  loading.value = true
  try {
    const res = await getRoles()
    roleList.value = res || []
  } catch (error) {
    console.error('加载角色失败:', error)
    ElMessage.error('加载角色列表失败')
  } finally {
    loading.value = false
  }
}

// 加载权限列表
async function loadPermissions() {
  try {
    const res = await getPermissions()
    allPermissions.value = res || []
  } catch (error) {
    console.error('加载权限失败:', error)
  }
}

// 新增
function showAddDialog() {
  dialogTitle.value = '新增角色'
  isEdit.value = false
  Object.assign(form, { ...defaultForm, permission_ids: [] })
  dialogVisible.value = true
}

// 编辑
function showEditDialog(row) {
  dialogTitle.value = '编辑角色'
  isEdit.value = true
  Object.assign(form, {
    name: row.name,
    display_name: row.display_name,
    description: row.description || '',
    sort_order: row.sort_order || 0,
    is_system: row.is_system,
    permission_ids: row.permissions?.map(p => p.id) || []
  })
  currentRole.value = row
  dialogVisible.value = true
}

// 提交表单
async function submitForm() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    const data = {
      display_name: form.display_name,
      description: form.description || null,
      sort_order: form.sort_order,
      permission_ids: form.permission_ids
    }

    if (isEdit.value) {
      await updateRole(currentRole.value.id, data)
      ElMessage.success('角色更新成功')
    } else {
      await createRole({ ...data, name: form.name })
      ElMessage.success('角色创建成功')
    }
    dialogVisible.value = false
    loadRoles()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    submitting.value = false
  }
}

// 删除
function handleDelete(row) {
  currentRole.value = row
  deleteDialogVisible.value = true
}

async function confirmDelete() {
  deleting.value = true
  try {
    await deleteRole(currentRole.value.id)
    ElMessage.success('删除成功')
    deleteDialogVisible.value = false
    loadRoles()
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error(error.response?.data?.detail || '删除失败')
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  loadRoles()
  loadPermissions()
})
</script>

<style scoped>
.page-container {
  padding: 0;
}

.search-card {
  margin-bottom: 0;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.permission-groups {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
}

.permission-group {
  margin-bottom: 15px;
}

.permission-group:last-child {
  margin-bottom: 0;
}

.group-title {
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}

.el-checkbox {
  margin-right: 20px;
  margin-bottom: 8px;
}
</style>
