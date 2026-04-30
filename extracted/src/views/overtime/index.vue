<template>
  <div class="overtime-page">
    <el-card class="search-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="6">
          <el-select v-model="filters.status" placeholder="审批状态" clearable style="width:100%" @change="fetchData">
            <el-option label="待审批" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-col>
        <el-col :span="12">
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
            <el-icon><Plus /></el-icon>申请加班
          </el-button>
          <el-button @click="fetchData"><el-icon><Refresh /></el-icon>刷新</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card style="margin-top:16px;">
      <el-table :data="list" v-loading="loading" style="width:100%">
        <el-table-column prop="employee_name" label="员工姓名" width="120" />
        <el-table-column prop="employee_no" label="工号" width="100" />
        <el-table-column prop="date" label="加班日期" width="120" />
        <el-table-column label="加班时间" width="180">
          <template #default="scope">
            {{ scope.row.start_time }} ~ {{ scope.row.end_time }}
          </template>
        </el-table-column>
        <el-table-column prop="hours" label="工时" width="80" align="center" />
        <el-table-column prop="reason" label="加班事由" min-width="150" show-overflow-tooltip />
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

    <el-dialog v-model="dialogVisible" title="申请加班" width="500px" destroy-on-close>
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
        <el-form-item label="加班日期" prop="date">
          <el-date-picker v-model="form.date" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="开始时间" prop="start_time">
              <el-time-picker v-model="form.start_time" format="HH:mm" value-format="HH:mm" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间" prop="end_time">
              <el-time-picker v-model="form.end_time" format="HH:mm" value-format="HH:mm" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="加班工时" prop="hours">
          <el-input v-model="form.hours" placeholder="例如：2.5" />
        </el-form-item>
        <el-form-item label="加班事由" prop="reason">
          <el-input v-model="form.reason" type="textarea" :rows="3" placeholder="请输入加班事由" />
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
import { getOvertimeRequests, createOvertimeRequest } from '@/api/leave'
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

const filters = reactive({ status: '', dateRange: [] })
const page = reactive({ current: 1, size: 20, total: 0 })

const statusMap = { pending: '待审批', approved: '已通过', rejected: '已拒绝' }

const form = reactive({
  employee_id: null,
  date: '',
  start_time: '18:00',
  end_time: '20:00',
  hours: '2.0',
  reason: ''
})

const rules = {
  employee_id: [{ required: true, message: '请选择员工', trigger: 'change' }],
  date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  hours: [{ required: true, message: '请输入工时', trigger: 'blur' }],
  reason: [{ required: true, message: '请输入加班事由', trigger: 'blur' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = { skip: (page.current - 1) * page.size, limit: page.size }
    if (filters.status) params.status = filters.status
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_date = filters.dateRange[0]
      params.end_date = filters.dateRange[1]
    }
    const res = await getOvertimeRequests(params)
    const data = Array.isArray(res) ? res : (res.items || [])
    list.value = data
    page.total = Array.isArray(res) ? res.length : (res.total || data.length)
  } catch (e) {
    ElMessage.error('加载加班记录失败')
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
  Object.assign(form, { employee_id: null, date: '', start_time: '18:00', end_time: '20:00', hours: '2.0', reason: '' })
  dialogVisible.value = true
}

const doLookup = async () => {
  if (!lookupKey.value.trim()) { lookupHint.value = '请输入工号或姓名'; return }
  lookingUp.value = true; lookupHint.value = ''
  try {
    const res = await lookupRoster(lookupKey.value.trim())
    if (!res) { lookupHint.value = '花名册中未找到此人'; return }
    lookupHint.value = `✓ 已找到：${res.姓名}（${res.工号}）-${res.部门}-${res.岗位 || '无岗位'}`
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
    await createOvertimeRequest({
      employee_id: form.employee_id,
      date: form.date,
      start_time: form.start_time,
      end_time: form.end_time,
      hours: form.hours,
      reason: form.reason
    })
    ElMessage.success('加班申请提交成功')
    dialogVisible.value = false
    fetchData()
  } catch (e) {
    ElMessage.error('提交失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定删除该加班申请？', '确认删除', { type: 'warning' })
    .then(() => {
      ElMessage.info('加班记录删除功能待实现')
    }).catch(() => {})
}

onMounted(() => { fetchData(); fetchEmployees() })
</script>

<style scoped>
.overtime-page { padding: 0; }
.search-card { margin-bottom: 0; }
</style>
