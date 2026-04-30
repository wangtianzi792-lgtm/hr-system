<template>
  <div class="reports-page">
    <el-card class="search-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="6">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width:100%"
            @change="fetchReport"
          />
        </el-col>
        <el-col :span="5">
          <el-select v-model="filters.department_id" placeholder="选择部门" clearable style="width:100%" @change="fetchReport">
            <el-option v-for="dept in departmentList" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="filters.employee_id" placeholder="选择员工" clearable style="width:100%" @change="fetchReport">
            <el-option v-for="emp in employeeList" :key="emp.id" :label="emp.name" :value="emp.id" />
          </el-select>
        </el-col>
        <el-col :span="8" style="text-align: right;">
          <el-button type="primary" @click="fetchReport" style="background:#ec6921;border-color:#ec6921;">
            <el-icon><Search /></el-icon>查询
          </el-button>
          <el-button @click="resetFilters"><el-icon><Refresh /></el-icon>重置</el-button>
          <el-button type="success" @click="exportData"><el-icon><Download /></el-icon>导出</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="16" style="margin-top:16px;">
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-value" style="color:#409EFF;">{{ summary.total_employees }}</div>
          <div class="stat-label">总人数</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-value" style="color:#67C23A;">{{ summary.actual_days_total }}</div>
          <div class="stat-label">实际出勤</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-value" style="color:#E6A23C;">{{ summary.late_total }}</div>
          <div class="stat-label">迟到次数</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-value" style="color:#F56C6C;">{{ summary.early_total }}</div>
          <div class="stat-label">早退次数</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-value" style="color:#909399;">{{ summary.absent_total }}</div>
          <div class="stat-label">缺勤天数</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-value" style="color:#ec6921;">{{ summary.attendance_rate }}%</div>
          <div class="stat-label">出勤率</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top:16px;">
      <el-table :data="reportList" v-loading="loading" style="width:100%" border>
        <el-table-column prop="employee_no" label="工号" width="100" />
        <el-table-column prop="employee_name" label="姓名" width="100" />
        <el-table-column prop="department_name" label="部门" width="120" />
        <el-table-column prop="position" label="职位" width="120" />
        <el-table-column prop="work_days" label="应出勤" width="90" align="center" />
        <el-table-column prop="actual_days" label="实出勤" width="90" align="center" />
        <el-table-column prop="normal_days" label="正常" width="90" align="center" />
        <el-table-column prop="late_count" label="迟到" width="80" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.late_count > 0" type="warning" size="small">{{ scope.row.late_count }}</el-tag>
            <span v-else>{{ scope.row.late_count }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="early_count" label="早退" width="80" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.early_count > 0" type="danger" size="small">{{ scope.row.early_count }}</el-tag>
            <span v-else>{{ scope.row.early_count }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="absent_days" label="缺勤" width="80" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.absent_days > 0" type="info" size="small">{{ scope.row.absent_days }}</el-tag>
            <span v-else>{{ scope.row.absent_days }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_work_hours" label="工时" width="100" align="center" />
        <el-table-column label="出勤率" width="100" align="center">
          <template #default="scope">
            <el-progress :percentage="getRate(scope.row)" :color="getRateColor(scope.row)" :stroke-width="8" />
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="page.current" v-model:page-size="page.size"
        :total="page.total" :page-sizes="[10,20,50]"
        layout="total,sizes,prev,pager,next"
        style="margin-top:16px;justify-content:flex-end;"
        @size-change="fetchReport" @current-change="fetchReport"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAttendanceReport } from '@/api/attendance'
import { getDepartments } from '@/api/departments'
import { getEmployees } from '@/api/employees'
import { exportDailyReport } from '@/utils/export'

const loading = ref(false)
const reportList = ref([])
const departmentList = ref([])
const employeeList = ref([])

const dateRange = ref([])
const filters = reactive({ department_id: '', employee_id: '' })
const page = reactive({ current: 1, size: 20, total: 0 })

const summary = reactive({
  total_employees: 0,
  actual_days_total: 0,
  late_total: 0,
  early_total: 0,
  absent_total: 0,
  attendance_rate: 0
})

const getRate = (row) => {
  if (!row.work_days || row.work_days === 0) return 0
  return Math.round((row.actual_days / row.work_days) * 100)
}

const getRateColor = (row) => {
  const rate = getRate(row)
  if (rate >= 95) return '#67C23A'
  if (rate >= 80) return '#E6A23C'
  return '#F56C6C'
}

const fetchReport = async () => {
  loading.value = true
  try {
    const params = {
      start_date: dateRange.value && dateRange.value[0] ? dateRange.value[0] : getDefaultStartDate(),
      end_date: dateRange.value && dateRange.value[1] ? dateRange.value[1] : getDefaultEndDate(),
      skip: (page.current - 1) * page.size,
      limit: page.size
    }
    if (filters.department_id) params.department_id = filters.department_id
    if (filters.employee_id) params.employee_id = filters.employee_id

    const res = await getAttendanceReport(params)
    const data = res.items || []
    reportList.value = data
    page.total = res.total || data.length

    summary.total_employees = data.length
    summary.actual_days_total = data.reduce((s, r) => s + (r.actual_days || 0), 0)
    summary.late_total = data.reduce((s, r) => s + (r.late_count || 0), 0)
    summary.early_total = data.reduce((s, r) => s + (r.early_count || 0), 0)
    summary.absent_total = data.reduce((s, r) => s + (r.absent_days || 0), 0)
    const totalWorkDays = data.reduce((s, r) => s + (r.work_days || 0), 0)
    summary.attendance_rate = totalWorkDays > 0 ? Math.round((summary.actual_days_total / totalWorkDays) * 100) : 0
  } catch (e) {
    console.error('加载报表失败', e)
    ElMessage.error('加载报表失败')
  } finally {
    loading.value = false
  }
}

const getDefaultStartDate = () => {
  const d = new Date()
  d.setDate(1)
  return d.toISOString().split('T')[0]
}

const getDefaultEndDate = () => {
  return new Date().toISOString().split('T')[0]
}

const resetFilters = () => {
  dateRange.value = []
  filters.department_id = ''
  filters.employee_id = ''
  page.current = 1
  fetchReport()
}

const exportData = () => {
  if (reportList.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }
  
  // 转换数据格式
  const exportData = reportList.value.map(row => ({
    employee_no: row.employee_no,
    name: row.employee_name,
    department: row.department_name,
    position: row.position,
    should_attend: row.work_days,
    actual_attend: row.actual_days,
    normal: row.normal_days,
    late: row.late_count,
    early: row.early_count,
    absent: row.absent_days,
    work_hours: row.total_work_hours,
    attendance_rate: getRate(row) + '%'
  }))
  
  exportDailyReport(exportData, dateRange.value)
  ElMessage.success('导出成功')
}

const fetchDepartmentsList = async () => {
  try {
    const res = await getDepartments({ limit: 100 })
    departmentList.value = Array.isArray(res) ? res : (res.items || [])
  } catch (e) { console.error('加载部门失败', e) }
}

const fetchEmployeesList = async () => {
  try {
    const res = await getEmployees({ limit: 1000 })
    employeeList.value = Array.isArray(res) ? res : (res.items || [])
  } catch (e) { console.error('加载员工失败', e) }
}

onMounted(() => {
  dateRange.value = [getDefaultStartDate(), getDefaultEndDate()]
  fetchReport()
  fetchDepartmentsList()
  fetchEmployeesList()
})
</script>

<style scoped>
.reports-page { padding: 0; }
.search-card { margin-bottom: 0; }
.stat-card { text-align: center; padding: 8px 0; }
.stat-value { font-size: 24px; font-weight: 700; line-height: 1.2; }
.stat-label { font-size: 12px; color: #999; margin-top: 4px; }
</style>
