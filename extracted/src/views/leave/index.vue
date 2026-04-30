<template>
  <div class="leave-page">
    <el-card class="search-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="5">
          <el-select v-model="filters.leave_type" placeholder="请假类型" clearable style="width:100%" @change="fetchData">
            <el-option label="年假" value="年假" />
            <el-option label="病假" value="病假" />
            <el-option label="事假" value="事假" />
            <el-option label="婚假" value="婚假" />
            <el-option label="产假" value="产假" />
            <el-option label="丧假" value="丧假" />
            <el-option label="调休" value="调休" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="filters.status" placeholder="审批状态" clearable style="width:100%" @change="fetchData">
            <el-option label="待审批" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width:100%"
            @change="fetchData"
          />
        </el-col>
        <el-col :span="6" style="text-align: right;">
          <el-button type="primary" @click="showDialog" style="background:#ec6921;border-color:#ec6921;">
            <el-icon><Plus /></el-icon>申请请假
          </el-button>
          <el-button @click="fetchData"><el-icon><Refresh /></el-icon>刷新</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card style="margin-top:16px;">
      <el-table :data="list" v-loading="loading" style="width:100%">
        <el-table-column prop="employee_name" label="员工姓名" width="120" />
        <el-table-column prop="employee_no" label="工号" width="100" />
        <el-table-column prop="department_name" label="部门" width="120" />
        <el-table-column prop="leave_type" label="请假类型" width="100">
          <template #default="scope">
            <el-tag size="small">{{ scope.row.leave_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="请假日期" width="220">
          <template #default="scope">
            {{ scope.row.start_date }} {{ scope.row.start_time || '' }} ~ {{ scope.row.end_date }} {{ scope.row.end_time || '' }}
          </template>
        </el-table-column>
        <el-table-column prop="total_days" label="天数" width="80" align="center" />
        <el-table-column prop="reason" label="请假事由" min-width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'approved' ? 'success' : scope.row.status === 'rejected' ? 'danger' : 'warning'" size="small">
              {{ statusMap[scope.row.status] || scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="page.current" v-model:page-size="page.size"
        :total="page.total" :page-sizes="[10,20,50]"
        layout="total,sizes,prev,pager,next"
        style="margin-top:16px;justify-content:flex-end;"
        @size-change="fetchData" @current-change="fetchData"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" title="申请请假" width="500px" destroy-on-close>
      <div v-if="!isEdit" style="background:#f5f7fa;border-radius:8px;padding:16px;margin-bottom:16px">
        <el-row :gutter="12">
          <el-col :span="16">
            <el-input v-model="lookupKey" placeholder="输入工号或姓名，从花名册自动带入信息" clearable @keyup.enter="doLookup" />
          </el-col>
          <el-col :span="8">
            <el-button type="primary" style="background-color:#ec6921;border-color:#ec6921" :loading="lookingUp" @click="doLookup">查找带入</el-button>
          </el-col>
        </el-row>
        <div v-if="lookupHint" style="margin-top:6px;font-size:12px;color:#999">{{ lookupHint }}</div>
      </div>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="选择员工" prop="employee_id">
          <el-select v-model="form.employee_id" style="width:100%" placeholder="选择员工" :disabled="!!lookupKey">
            <el-option v-for="emp in employeeList" :key="emp.id" :label="emp.name + ' (' + emp.employee_no + ')'" :value="emp.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="请假类型" prop="leave_type">
          <el-select v-model="form.leave_type" style="width:100%">
            <el-option label="年假" value="年假" />
            <el-option label="病假" value="病假" />
            <el-option label="事假" value="事假" />
            <el-option label="婚假" value="婚假" />
            <el-option label="产假" value="产假" />
            <el-option label="丧假" value="丧假" />
            <el-option label="调休" value="调休" />
          </el-select>
        </el-form-item>
        <el-form-item label="请假日期" prop="dateRange">
          <el-date-picker
            v-model="form.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width:100%"
          />
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-time-select
            v-model="form.start_time"
            start="08:00"
            step="00:30"
            end="22:00"
            placeholder="选择开始时间"
            style="width:100%"
          />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-time-select
            v-model="form.end_time"
            start="08:00"
            step="00:30"
            end="22:00"
            placeholder="选择结束时间"
            style="width:100%"
          />
        </el-form-item>
        <el-form-item label="请假天数" prop="total_days">
          <el-input-number v-model="form.total_days" :min="0.5" :max="365" :step="0.5" style="width:100%" />
        </el-form-item>
        <el-form-item label="请假事由" prop="reason">
          <el-input v-model="form.reason" type="textarea" :rows="3" placeholder="请输入请假事由" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="submit" :loading="submitLoading" style="background:#ec6921;border-color:#ec6921;">提交申请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getLeaveRequests, createLeaveRequest, deleteLeaveRequest } from '@/api/leave'
import { getEmployees } from '@/api/employees'
import { lookupRoster } from '@/api/roster'

const list = ref([])
const employeeList = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)
const lookupKey = ref('')
const lookingUp = ref(false)
const lookupHint = ref('')
const isEdit = ref(false)

const filters = reactive({ leave_type: '', status: '', dateRange: [] })
const page = reactive({ current: 1, size: 20, total: 0 })

const statusMap = { pending: '待审批', approved: '已通过', rejected: '已拒绝' }

const form = reactive({
  employee_id: null,
  leave_type: '',
  dateRange: [],
  start_time: '',
  end_time: '',
  total_days: 1,
  reason: ''
})

const rules = {
  employee_id: [{ required: true, message: '请选择员工', trigger: 'change' }],
  leave_type: [{ required: true, message: '请选择请假类型', trigger: 'change' }],
  dateRange: [{ required: true, message: '请选择日期范围', trigger: 'change' }],
  total_days: [{ required: true, message: '请输入天数', trigger: 'blur' }],
  reason: [{ required: true, message: '请输入请假事由', trigger: 'blur' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = { skip: (page.current - 1) * page.size, limit: page.size }
    if (filters.leave_type) params.leave_type = filters.leave_type
    if (filters.status) params.status = filters.status
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_date = filters.dateRange[0]
      params.end_date = filters.dateRange[1]
    }
    const res = await getLeaveRequests(params)
    const data = Array.isArray(res) ? res : (res.items || [])
    list.value = data
    page.total = Array.isArray(res) ? res.length : (res.total || data.length)
  } catch (e) {
    ElMessage.error('加载请假记录失败')
  } finally {
    loading.value = false
  }
}

const fetchEmployees = async () => {
  try {
    const res = await getEmployees({ limit: 1000 })
    employeeList.value = Array.isArray(res) ? res : (res.items || [])
  } catch (e) { console.error('加载员工失败', e) }
}

const showDialog = () => {
  lookupKey.value = ''; lookupHint.value = ''; isEdit.value = false
  Object.assign(form, { employee_id: null, leave_type: '', dateRange: [], start_time: '', end_time: '', total_days: 1, reason: '' })
  dialogVisible.value = true
}

const doLookup = async () => {
  if (!lookupKey.value.trim()) { lookupHint.value = '请输入工号或姓名'; return }
  lookingUp.value = true; lookupHint.value = ''
  try {
    const res = await lookupRoster(lookupKey.value.trim())
    if (!res) { lookupHint.value = '花名册中未找到此人'; return }
    lookupHint.value = `✓ 已找到：${res.姓名}（${res.工号}）-${res.部门}-${res.岗位 || '无岗位'}`
    // 根据工号匹配 employee_id
    const emp = employeeList.value.find(e => e.工号 === res.工号)
    if (emp) {
      form.employee_id = emp.id
    } else {
      form.employee_id = null
      lookupHint.value += '（未在系统中找到匹配员工，请手动选择）'
    }
  } catch (e) { lookupHint.value = '查找失败，请重试' } finally { lookingUp.value = false }
}

const submit = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    await createLeaveRequest({
      employee_id: form.employee_id,
      leave_type: form.leave_type,
      start_date: form.dateRange[0],
      end_date: form.dateRange[1],
      start_time: form.start_time,
      end_time: form.end_time,
      total_days: form.total_days,
      reason: form.reason
    })
    ElMessage.success('请假申请提交成功')
    dialogVisible.value = false
    fetchData()
  } catch (e) {
    ElMessage.error('提交失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定删除该请假申请？', '确认删除', { type: 'warning' })
    .then(async () => {
      try {
        await deleteLeaveRequest(row.id)
        ElMessage.success('删除成功')
        fetchData()
      } catch (e) {
        ElMessage.error('删除失败')
      }
    }).catch(() => {})
}

onMounted(() => { fetchData(); fetchEmployees() })
</script>

<style scoped>
.leave-page { padding: 0; }
.search-card { margin-bottom: 0; }
</style>
