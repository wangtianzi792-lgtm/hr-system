<template>
  <div class="page-container">
    <!-- 搜索和操作栏 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索部门名称/编码"
            clearable
            @clear="loadDepartments"
            @keyup.enter="loadDepartments"
          >
            <template #append>
              <el-button @click="loadDepartments">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterActive" placeholder="状态" clearable @change="loadDepartments">
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
        </el-col>
        <el-col :span="14" style="text-align: right;">
          <el-button type="primary" @click="showAddDialog" style="background-color: #ec6921; border-color: #ec6921;">
            <el-icon><Plus /></el-icon>新增部门
          </el-button>
          <el-button @click="refreshList">
            <el-icon><Refresh /></el-icon>刷新
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 部门列表 -->
    <el-card style="margin-top: 20px;">
      <el-table :data="departmentList" v-loading="loading" style="width: 100%" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="部门名称" min-width="150" />
        <el-table-column prop="code" label="部门编码" width="120" />
        <el-table-column prop="parent_name" label="上级部门" width="150">
          <template #default="scope">
            {{ scope.row.parent_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="manager_name" label="负责人" width="100">
          <template #default="scope">
            {{ scope.row.manager_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="employee_count" label="员工数" width="100" sortable />
        <el-table-column prop="sort_order" label="排序" width="100" sortable />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active === 1 ? 'success' : 'info'" size="small">
              {{ scope.row.is_active === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" link size="small" @click="showEditDialog(scope.row)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(scope.row)">
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入部门名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="部门编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入部门编码（可选）" maxlength="20" />
        </el-form-item>
        <el-form-item label="上级部门" prop="parent_id">
          <el-select
            v-model="form.parent_id"
            placeholder="选择上级部门（可选）"
            clearable
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="dept in departmentList.filter(d => d.id !== form.id)"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人" prop="manager_id">
          <el-select
            v-model="form.manager_id"
            placeholder="选择负责人（可选）"
            clearable
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="emp in employeeOptions"
              :key="emp.id"
              :label="`${emp.name} - ${emp.position || '未设置职位'}`"
              :value="emp.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" :max="9999" />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-radio-group v-model="form.is_active">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog v-model="deleteDialogVisible" title="确认删除" width="400px">
      <p>确定要删除部门 <strong>{{ currentDept?.name }}</strong> 吗？</p>
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getDepartments, createDepartment, updateDepartment, deleteDepartment } from '@/api/departments'
import { getEmployees } from '@/api/employees'

const loading = ref(false)
const submitting = ref(false)
const deleting = ref(false)
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const formRef = ref(null)
const dialogTitle = ref('')
const currentDept = ref(null)
const departmentList = ref([])
const employeeOptions = ref([])

const searchQuery = ref('')
const filterActive = ref(null)

const defaultForm = {
  name: '',
  code: '',
  parent_id: null,
  manager_id: null,
  sort_order: 0,
  is_active: 1,
  description: ''
}

const form = reactive({ ...defaultForm })

const rules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }]
}

// 加载部门列表
const loadDepartments = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value) params.keyword = searchQuery.value
    if (filterActive.value !== null) params.is_active = filterActive.value

    const res = await getDepartments(params)
    departmentList.value = res || []
  } catch (error) {
    console.error('加载部门失败:', error)
    ElMessage.error('加载部门列表失败')
  } finally {
    loading.value = false
  }
}

// 加载员工列表（用于选择负责人）
const loadEmployees = async () => {
  try {
    const res = await getEmployees({ limit: 1000 })
    employeeOptions.value = res.data || []
  } catch (error) {
    console.error('加载员工失败:', error)
  }
}

// 新增
const showAddDialog = () => {
  dialogTitle.value = '新增部门'
  Object.assign(form, defaultForm)
  dialogVisible.value = true
}

// 编辑
const showEditDialog = (row) => {
  dialogTitle.value = '编辑部门'
  Object.assign(form, {
    name: row.name,
    code: row.code || '',
    parent_id: row.parent_id,
    manager_id: row.manager_id,
    sort_order: row.sort_order || 0,
    is_active: row.is_active,
    description: row.description || ''
  })
  currentDept.value = row
  dialogVisible.value = true
}

// 提交表单
const submitForm = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    const data = { ...form }
    if (!data.code) data.code = null
    if (!data.parent_id) data.parent_id = null
    if (!data.manager_id) data.manager_id = null
    if (!data.description) data.description = null

    if (currentDept.value) {
      await updateDepartment(currentDept.value.id, data)
      ElMessage.success('部门更新成功')
    } else {
      await createDepartment(data)
      ElMessage.success('部门创建成功')
    }
    dialogVisible.value = false
    loadDepartments()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    submitting.value = false
  }
}

// 删除
const handleDelete = (row) => {
  currentDept.value = row
  deleteDialogVisible.value = true
}

const confirmDelete = async () => {
  deleting.value = true
  try {
    await deleteDepartment(currentDept.value.id)
    ElMessage.success('删除成功')
    deleteDialogVisible.value = false
    loadDepartments()
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error(error.response?.data?.detail || '删除失败')
  } finally {
    deleting.value = false
  }
}

// 刷新
const refreshList = () => {
  searchQuery.value = ''
  filterActive.value = null
  loadDepartments()
}

onMounted(() => {
  loadDepartments()
  loadEmployees()
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
</style>
