<template>
  <div class="onboarding-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>入职管理</span>
          <el-button type="primary" style="background-color:#ec6921;border-color:#ec6921" @click="showAddDialog">
            新增入职
          </el-button>
        </div>
      </template>

      <!-- 筛选栏 -->
      <el-row :gutter="20" style="margin-bottom:16px">
        <el-col :span="6">
          <el-input v-model="searchQuery" placeholder="搜索工号/姓名" clearable @keyup.enter="loadData" />
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterDept" placeholder="按部门筛选" clearable style="width:100%">
            <el-option v-for="d in deptOptions" :key="d" :label="d" :value="d" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterStatus" placeholder="按状态筛选" clearable style="width:100%">
            <el-option label="待入职" value="pending" />
            <el-option label="已入职" value="confirmed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" style="background-color:#ec6921;border-color:#ec6921" @click="loadData">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>

      <!-- 表格 -->
      <el-table :data="filteredList" v-loading="loading" stripe style="width:100%">
        <el-table-column prop="工号" label="工号" width="120" />
        <el-table-column prop="姓名" label="姓名" width="100" />
        <el-table-column prop="性别" label="性别" width="60" />
        <el-table-column prop="部门" label="部门" min-width="120" />
        <el-table-column prop="岗位" label="岗位" min-width="120" />
        <el-table-column prop="入职日期" label="计划入职日期" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.状态)">{{ statusText(row.状态) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="登记人" label="登记人" width="100" />
        <el-table-column prop="登记日期" label="登记日期" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="editRow(row)">编辑</el-button>
            <el-button type="danger" link @click="deleteRow(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div style="margin-top:16px;display:flex;justify-content:flex-end">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[30,50,100]"
          :total="total"
          layout="total,sizes,prev,pager,next"
          @current-change="loadData"
          @size-change="loadData"
        />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑入职信息' : '新增入职'" width="600px" destroy-on-close>
      <el-form :model="form" label-width="120px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="工号"><el-input v-model="form.工号" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名"><el-input v-model="form.姓名" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="form.性别" style="width:100%">
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话"><el-input v-model="form.联系电话" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="部门">
              <el-select v-model="form.部门" style="width:100%">
                <el-option v-for="d in deptOptions" :key="d" :label="d" :value="d" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="岗位"><el-input v-model="form.岗位" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="入职日期">
              <el-date-picker v-model="form.入职日期" type="date" value-format="YYYY-MM-DD" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.状态" style="width:100%">
                <el-option label="待入职" value="pending" />
                <el-option label="已入职" value="confirmed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注"><el-input v-model="form.备注" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" style="background-color:#ec6921;border-color:#ec6921" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRosterDepartments } from '@/api/roster'
import { getOnboardingList, createOnboarding, updateOnboarding, deleteOnboarding } from '@/api/onboarding'

const searchQuery = ref('')
const filterDept = ref('')
const filterStatus = ref('')
const deptOptions = ref([])
const page = ref(1)
const pageSize = ref(30)
const total = ref(0)
const loading = ref(false)
const allData = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)

const form = ref({
  工号: '', 姓名: '', 性别: '男', 联系电话: '', 部门: '', 岗位: '', 入职日期: '', 状态: 'pending', 备注: ''
})

const filteredList = computed(() => {
  let list = allData.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(r =>
      (r.工号 && r.工号.toLowerCase().includes(q)) ||
      (r.姓名 && r.姓名.toLowerCase().includes(q))
    )
  }
  if (filterDept.value) list = list.filter(r => r.部门 === filterDept.value)
  if (filterStatus.value) list = list.filter(r => r.状态 === filterStatus.value)
  return list
})

const statusText = (s) => ({ pending: '待入职', confirmed: '已入职', cancelled: '已取消' }[s] || s)
const statusType = (s) => ({ pending: 'warning', confirmed: 'success', cancelled: 'info' }[s] || '')

const loadData = async () => {
  loading.value = true
  try {
    const res = await getOnboardingList({
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchQuery.value || undefined,
      department: filterDept.value || undefined,
      status: filterStatus.value || undefined,
    })
    allData.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  filterDept.value = ''
  filterStatus.value = ''
  page.value = 1
  loadData()
}

const showAddDialog = () => {
  isEdit.value = false
  Object.keys(form.value).forEach(k => {
    if (k === '性别') form.value[k] = '男'
    else if (k === '状态') form.value[k] = 'pending'
    else form.value[k] = ''
  })
  dialogVisible.value = true
}

const editRow = (row) => {
  isEdit.value = true
  Object.keys(form.value).forEach(k => form.value[k] = row[k] || '')
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    if (isEdit.value) {
      await updateOnboarding(form.value)
      ElMessage.success('更新成功')
    } else {
      await createOnboarding(form.value)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const deleteRow = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除 "${row.姓名}" 的入职记录吗？`, '确认', { type: 'warning' })
    await deleteOnboarding(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadData()
  getRosterDepartments().then(res => { deptOptions.value = res || [] }).catch(() => {})
})
</script>

<style scoped>
.onboarding-container { padding: 0; }
.card-header { display:flex; justify-content:space-between; align-items:center; }
</style>
