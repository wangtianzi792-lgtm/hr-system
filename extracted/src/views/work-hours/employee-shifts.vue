<template>
  <div class="employee-shifts-page">
    <div class="page-header">
      <h2>员工排班</h2>
      <p class="subtitle">为员工绑定当月班次，可按员工类型筛选</p>
    </div>

    <!-- 筛选区 -->
    <el-card style="margin-bottom:16px">
      <div class="filter-row">
        <el-select v-model="filterMonth" placeholder="选择月份" style="width:140px" @change="loadData">
          <el-option v-for="m in monthOptions" :key="m" :label="m" :value="m" />
        </el-select>
        <el-select v-model="filterType" placeholder="员工类型" clearable style="width:140px" @change="loadData">
          <el-option label="正式工" value="正式工" />
          <el-option label="派遣工" value="派遣工" />
          <el-option label="退休返聘" value="退休返聘" />
        </el-select>
        <el-select v-model="filterDept" placeholder="全部部门" clearable style="width:160px" @change="loadData">
          <el-option v-for="d in departments" :key="d" :label="d" :value="d" />
        </el-select>
        <el-input v-model="keyword" placeholder="搜索姓名/工号" clearable style="width:160px" @change="loadData" />
      </div>
    </el-card>

    <!-- 已排班列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>已排班员工（{{ assigned.length }}人）</span>
          <el-button type="primary" size="small" @click="openAssignDialog">
            <el-icon><Plus /></el-icon> 批量绑定班次
          </el-button>
        </div>
      </template>

      <el-table :data="assigned" stripe max-height="400">
        <el-table-column prop="工号" label="工号" width="120" />
        <el-table-column prop="姓名" label="姓名" width="100" />
        <el-table-column prop="岗位" label="岗位" min-width="120" />
        <el-table-column prop="员工类型" label="类型" width="90">
          <template #default="{ row }">
            <el-tag v-if="row.员工类型==='正式工'" size="small" type="success">{{ row.员工类型 }}</el-tag>
            <el-tag v-else-if="row.员工类型==='派遣工'" size="small" type="warning">{{ row.员工类型 }}</el-tag>
            <span v-else style="color:#666">{{ row.员工类型 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="shift_name" label="班次" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.shift_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="班次时间" width="160">
          <template #default="{ row }">
            {{ row.start_time }} ~ {{ row.end_time }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openAssignDialog(row)">更换</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 未排班员工（提示） -->
    <el-card style="margin-top:16px" v-if="unassigned.length > 0">
      <template #header>
        <span>未排班员工（{{ unassigned.length }}人）</span>
      </template>
      <div style="display:flex;flex-wrap:wrap;gap:8px">
        <el-tag v-for="e in unassigned.slice(0,30)" :key="e.工号" size="small" type="info">{{ e.姓名 }}</el-tag>
        <span v-if="unassigned.length > 30" style="color:#999">...还有{{ unassigned.length-30 }}人</span>
      </div>
    </el-card>

    <!-- 绑定班次弹窗 -->
    <el-dialog v-model="dialogVisible" title="绑定班次" width="500px">
      <div v-if="!assigning">
        <el-form :model="assignForm" label-width="100px">
          <el-form-item label="选择员工">
            <el-select v-model="assignForm.employee_no" placeholder="搜索员工" filterable style="width:100%">
              <el-option v-for="e in availableEmployees" :key="e.工号" :label="`${e.姓名}（${e.工号}）`" :value="e.工号" />
            </el-select>
          </el-form-item>
          <el-form-item label="生效月份">
            <el-input v-model="assignForm.effective_month" placeholder="格式：2025-05" style="width:100%" />
          </el-form-item>
          <el-form-item label="选择班次">
            <el-select v-model="assignForm.shift_id" placeholder="请选择班次" style="width:100%">
              <el-option v-for="s in shifts" :key="s.id" :label="`${s.name}（${s.start_time}~${s.end_time}）`" :value="s.id" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAssignment">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { get, post } from '@/api/request'

const filterMonth = ref(new Date().getFullYear() + '-' + String(new Date().getMonth()+1).padStart(2,'0'))
const filterType = ref('')
const filterDept = ref('')
const keyword = ref('')

const assigned = ref([])      // 已排班员工
const unassigned = ref([])     // 未排班员工
const shifts = ref([])
const departments = ref([])
const employees = ref([])
const dialogVisible = ref(false)
const assigning = ref({})
const availableEmployees = computed(() => employees.value)

const assignForm = ref({ employee_no: '', shift_id: '', effective_month: '' })

const monthOptions = computed(() => {
  const opts = []
  const now = new Date()
  for (let i = -1; i < 3; i++) {
    const d = new Date(now.getFullYear(), now.getMonth() + i, 1)
    opts.push(d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0'))
  }
  return opts
})

const loadShifts = async () => {
  const res = await get('/api/work-hours/shifts')
  shifts.value = res.items || []
}

const loadRoster = async () => {
  const params = new URLSearchParams({ status: 'all', limit: 1000 })
  if (filterType.value) params.set('employee_type', filterType.value)
  const res = await get('/api/roster/?' + params.toString())
  employees.value = res.items || []
  departments.value = [...new Set(employees.value.map(e => e.部门).filter(Boolean))]
}

const loadData = async () => {
  await Promise.all([loadShifts(), loadRoster()])

  // 加载已排班
  const res = await get(`/api/work-hours/employee-shifts?month=${filterMonth.value}`)
  assigned.value = res.items || []

  // 未排班员工 = 花名册 - 已排班
  const assignedNos = new Set(assigned.value.map(a => a.employee_no))
  let pool = employees.value
  if (filterType.value) pool = pool.filter(e => e.员工类型 === filterType.value)
  if (filterDept.value) pool = pool.filter(e => e.部门 === filterDept.value)
  if (keyword.value) pool = pool.filter(e => e.姓名.includes(keyword.value) || e.工号.includes(keyword.value))
  unassigned.value = pool.filter(e => e.是否在职 === 1 && !assignedNos.has(e.工号))
}

const openAssignDialog = (row = null) => {
  if (row) {
    assignForm.value = { employee_no: row.employee_no, shift_id: row.shift_id, effective_month: filterMonth.value }
  } else {
    assignForm.value = { employee_no: '', shift_id: '', effective_month: filterMonth.value }
  }
  dialogVisible.value = true
}

const saveAssignment = async () => {
  if (!assignForm.value.employee_no) { ElMessage.warning('请选择员工'); return }
  if (!assignForm.value.shift_id) { ElMessage.warning('请选择班次'); return }
  if (!assignForm.value.effective_month) { ElMessage.warning('请填写生效月份'); return }
  await post('/api/work-hours/employee-shifts', assignForm.value)
  ElMessage.success('排班已保存')
  dialogVisible.value = false
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.employee-shifts-page { padding: 24px; }
.page-header { margin-bottom: 20px; }
.page-header h2 { margin: 0 0 4px; font-size: 18px; color: #333; }
.subtitle { margin: 0; font-size: 13px; color: #999; }
.filter-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
