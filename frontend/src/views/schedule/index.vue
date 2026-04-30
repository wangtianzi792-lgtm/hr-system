<template>
  <div class="schedule-page">
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
            @change="fetchSchedules"
          />
        </el-col>
        <el-col :span="6">
          <el-select v-model="filterDepartment" placeholder="选择部门" clearable style="width:100%" @change="fetchSchedules">
            <el-option v-for="dept in departmentList" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input v-model="filterEmployee" placeholder="搜索员工姓名" clearable @keyup.enter="fetchSchedules">
            <template #append>
              <el-button @click="fetchSchedules"><el-icon><Search /></el-icon></el-button>
            </template>
          </el-input>
        </el-col>
        <el-col :span="6" style="text-align: right;">
          <el-button type="primary" @click="showBatchDialog" style="background:#ec6921;border-color:#ec6921;">
            <el-icon><Plus /></el-icon>批量排班
          </el-button>
          <el-button @click="fetchSchedules"><el-icon><Refresh /></el-icon>刷新</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card style="margin-top:16px;">
      <el-table :data="scheduleList" v-loading="loading" style="width:100%" border>
        <el-table-column prop="employee_name" label="员工姓名" width="120" fixed />
        <el-table-column prop="employee_no" label="工号" width="100" />
        <el-table-column prop="department_name" label="部门" width="120" />
        <el-table-column prop="schedule_date" label="排班日期" width="120" />
        <el-table-column prop="shift_name" label="班次" width="120">
          <template #default="scope">
            <el-tag v-if="scope.row.shift_name" :color="scope.row.shift_color || '#409EFF'" effect="dark" size="small">
              {{ scope.row.shift_name }}
            </el-tag>
            <span v-else style="color:#999;">休息</span>
          </template>
        </el-table-column>
        <el-table-column label="上班时间" width="150">
          <template #default="scope">
            <span v-if="scope.row.check_in_start">{{ scope.row.check_in_start }} ~ {{ scope.row.check_in_end }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="下班时间" width="150">
          <template #default="scope">
            <span v-if="scope.row.check_out_start">{{ scope.row.check_out_start }} ~ {{ scope.row.check_out_end }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'scheduled' ? 'success' : scope.row.status === 'leave' ? 'warning' : 'info'" size="small">
              {{ statusMap[scope.row.status] || scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="editSchedule(scope.row)" style="color:#ec6921;">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="currentPage" v-model:page-size="pageSize"
        :total="total" :page-sizes="[10,20,50]"
        layout="total,sizes,prev,pager,next"
        style="margin-top:16px;justify-content:flex-end;"
        @size-change="fetchSchedules" @current-change="fetchSchedules"
      />
    </el-card>

    <!-- 批量排班对话框 -->
    <el-dialog v-model="batchDialogVisible" title="批量排班" width="600px">
      <el-form :model="batchForm" :rules="batchRules" ref="batchFormRef" label-width="120px">
        <el-form-item label="排班对象" prop="targetType">
          <el-radio-group v-model="batchForm.targetType">
            <el-radio label="department">按部门</el-radio>
            <el-radio label="employee">按员工</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="batchForm.targetType === 'department'" label="选择部门" prop="departmentIds">
          <el-select v-model="batchForm.departmentIds" multiple style="width:100%" placeholder="选择部门">
            <el-option v-for="dept in departmentList" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-else label="选择员工" prop="employeeIds">
          <el-select v-model="batchForm.employeeIds" multiple style="width:100%" placeholder="选择员工">
            <el-option v-for="emp in employeeList" :key="emp.id" :label="emp.name + ' (' + emp.employee_no + ')'" :value="emp.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="排班日期" prop="dateRange">
          <el-date-picker
            v-model="batchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width:100%"
          />
        </el-form-item>
        <el-form-item label="选择班次" prop="shiftId">
          <el-select v-model="batchForm.shiftId" style="width:100%" placeholder="选择班次">
            <el-option v-for="shift in shiftList" :key="shift.id" :label="shift.name" :value="shift.id">
              <span :style="{ color: shift.color || '#409EFF' }">●</span> {{ shift.name }}
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="工作日">
          <el-checkbox-group v-model="batchForm.weekDays">
            <el-checkbox :label="1">周一</el-checkbox>
            <el-checkbox :label="2">周二</el-checkbox>
            <el-checkbox :label="3">周三</el-checkbox>
            <el-checkbox :label="4">周四</el-checkbox>
            <el-checkbox :label="5">周五</el-checkbox>
            <el-checkbox :label="6">周六</el-checkbox>
            <el-checkbox :label="0">周日</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchDialogVisible=false">取消</el-button>
        <el-button type="primary" @click="submitBatch" :loading="submitLoading" style="background:#ec6921;border-color:#ec6921;">确认排班</el-button>
      </template>
    </el-dialog>

    <!-- 编辑排班对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑排班" width="500px">
      <el-form :model="editForm" ref="editFormRef" label-width="100px">
        <el-form-item label="员工">
          <span>{{ editForm.employee_name }}</span>
        </el-form-item>
        <el-form-item label="排班日期">
          <span>{{ editForm.schedule_date }}</span>
        </el-form-item>
        <el-form-item label="班次">
          <el-select v-model="editForm.shift_id" style="width:100%" placeholder="选择班次">
            <el-option label="休息" :value="null" />
            <el-option v-for="shift in shiftList" :key="shift.id" :label="shift.name" :value="shift.id">
              <span :style="{ color: shift.color || '#409EFF' }">●</span> {{ shift.name }}
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status" style="width:100%">
            <el-option label="已排班" value="scheduled" />
            <el-option label="请假" value="leave" />
            <el-option label="调休" value="dayoff" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.remark" type="textarea" :rows="2" placeholder="备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible=false">取消</el-button>
        <el-button type="primary" @click="submitEdit" :loading="submitLoading" style="background:#ec6921;border-color:#ec6921;">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSchedules, createSchedule, deleteSchedule, batchSchedule } from '@/api/shifts'
import { getShifts } from '@/api/shifts'
import { getDepartments } from '@/api/departments'
import { getEmployees } from '@/api/employees'

const scheduleList = ref([])
const shiftList = ref([])
const departmentList = ref([])
const employeeList = ref([])
const loading = ref(false)

const dateRange = ref([])
const filterDepartment = ref('')
const filterEmployee = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const batchDialogVisible = ref(false)
const editDialogVisible = ref(false)
const submitLoading = ref(false)
const batchFormRef = ref(null)
const editFormRef = ref(null)

const statusMap = {
  scheduled: '已排班',
  leave: '请假',
  dayoff: '调休'
}

const batchForm = reactive({
  targetType: 'department',
  departmentIds: [],
  employeeIds: [],
  dateRange: [],
  shiftId: null,
  weekDays: [1, 2, 3, 4, 5]
})

const batchRules = {
  targetType: [{ required: true, message: '请选择排班对象', trigger: 'change' }],
  dateRange: [{ required: true, message: '请选择日期范围', trigger: 'change' }],
  shiftId: [{ required: true, message: '请选择班次', trigger: 'change' }]
}

const editForm = reactive({
  id: null,
  employee_name: '',
  schedule_date: '',
  shift_id: null,
  status: 'scheduled',
  remark: ''
})

const fetchSchedules = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    if (filterDepartment.value) {
      params.department_id = filterDepartment.value
    }
    if (filterEmployee.value) {
      params.employee_name = filterEmployee.value
    }
    const res = await getSchedules(params)
    const data = Array.isArray(res) ? res : (res.items || [])
    scheduleList.value = data
    total.value = Array.isArray(res) ? res.length : (res.total || data.length)
  } catch (e) {
    ElMessage.error('加载排班表失败')
  } finally {
    loading.value = false
  }
}

const fetchShiftsList = async () => {
  try {
    const res = await getShifts({ limit: 100 })
    shiftList.value = Array.isArray(res) ? res : (res.items || [])
  } catch (e) {
    console.error('加载班次失败', e)
  }
}

const fetchDepartments = async () => {
  try {
    const res = await getDepartments()
    departmentList.value = Array.isArray(res) ? res : (res.items || [])
  } catch (e) {
    console.error('加载部门失败', e)
  }
}

const fetchEmployees = async () => {
  try {
    const res = await getEmployees({ limit: 1000 })
    employeeList.value = Array.isArray(res) ? res : (res.items || [])
  } catch (e) {
    console.error('加载员工失败', e)
  }
}

const showBatchDialog = () => {
  batchForm.targetType = 'department'
  batchForm.departmentIds = []
  batchForm.employeeIds = []
  batchForm.dateRange = []
  batchForm.shiftId = null
  batchForm.weekDays = [1, 2, 3, 4, 5]
  batchDialogVisible.value = true
}

const submitBatch = async () => {
  const valid = await batchFormRef.value?.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    const data = {
      start_date: batchForm.dateRange[0],
      end_date: batchForm.dateRange[1],
      shift_id: batchForm.shiftId,
      week_days: batchForm.weekDays.join(',')
    }
    if (batchForm.targetType === 'department') {
      data.department_ids = batchForm.departmentIds
    } else {
      data.employee_ids = batchForm.employeeIds
    }
    await batchSchedule(data)
    ElMessage.success('批量排班成功')
    batchDialogVisible.value = false
    fetchSchedules()
  } catch (e) {
    ElMessage.error('批量排班失败')
  } finally {
    submitLoading.value = false
  }
}

const editSchedule = (row) => {
  Object.assign(editForm, {
    id: row.id,
    employee_name: row.employee_name,
    schedule_date: row.schedule_date,
    shift_id: row.shift_id,
    status: row.status || 'scheduled',
    remark: row.remark || ''
  })
  editDialogVisible.value = true
}

const submitEdit = async () => {
  submitLoading.value = true
  try {
    await createSchedule({
      id: editForm.id,
      shift_id: editForm.shift_id,
      status: editForm.status,
      remark: editForm.remark
    })
    ElMessage.success('排班已更新')
    editDialogVisible.value = false
    fetchSchedules()
  } catch (e) {
    ElMessage.error('更新失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定删除该排班记录？', '确认删除', { type: 'warning' })
    .then(async () => {
      try {
        await deleteSchedule(row.id)
        ElMessage.success('删除成功')
        fetchSchedules()
      } catch (e) {
        ElMessage.error('删除失败')
      }
    }).catch(() => {})
}

onMounted(() => {
  fetchSchedules()
  fetchShiftsList()
  fetchDepartments()
  fetchEmployees()
})
</script>

<style scoped>
.schedule-page { padding: 0; }
.search-card { margin-bottom: 0; }
</style>
