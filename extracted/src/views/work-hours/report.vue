<template>
  <div class="report-page">
    <div class="page-header">
      <h2>工时报表</h2>
      <p class="subtitle">日工时明细及月度汇总，正式工与派遣工分开统计</p>
    </div>

    <!-- 筛选区 -->
    <el-card style="margin-bottom:16px">
      <div class="filter-row">
        <el-select v-model="queryMonth" placeholder="月份" style="width:140px" @change="loadReport">
          <el-option v-for="m in monthOptions" :key="m" :label="m" :value="m" />
        </el-select>
        <el-select v-model="queryType" placeholder="员工类型" clearable style="width:130px" @change="loadReport">
          <el-option label="正式工" value="正式工" />
          <el-option label="派遣工" value="派遣工" />
        </el-select>
        <el-select v-model="queryDept" placeholder="部门" clearable style="width:160px" @change="loadReport">
          <el-option v-for="d in departments" :key="d" :label="d" :value="d" />
        </el-select>
        <el-input v-model="keyword" placeholder="搜索姓名/工号" clearable style="width:150px" @change="loadReport" />
        <el-button type="primary" @click="loadReport">查询</el-button>
        <el-button @click="exportExcel" :loading="exporting">导出Excel</el-button>
      </div>
    </el-card>

    <!-- 月度汇总 -->
    <el-card style="margin-bottom:16px" v-if="summary.length > 0">
      <template #header>
        <span>月度汇总</span>
      </template>
      <el-table :data="summary" stripe size="small">
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="employee_no" label="工号" width="110" />
        <el-table-column prop="employee_type" label="类型" width="90">
          <template #default="{ row }">
            <el-tag v-if="row.employee_type==='正式工'" size="small" type="success">正式工</el-tag>
            <el-tag v-else-if="row.employee_type==='派遣工'" size="small" type="warning">派遣工</el-tag>
            <span v-else>{{ row.employee_type }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="regular_hours" label="正常工时" width="100">
          <template #default="{ row }">{{ row.regular_hours }}h</template>
        </el-table-column>
        <el-table-column prop="overtime_hours" label="加班工时" width="100">
          <template #default="{ row }">
            <span style="color:#ec6921">{{ row.overtime_hours }}h</span>
          </template>
        </el-table-column>
        <el-table-column prop="leave_hours" label="请假工时" width="100">
          <template #default="{ row }">
            <span style="color:#999">{{ row.leave_hours }}h</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_hours" label="合计" width="100">
          <template #default="{ row }"><b>{{ row.total_hours }}h</b></template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="showDetail(row)">日工时明细</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 日工时明细 -->
    <el-card v-if="currentEmployee">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>{{ currentEmployee.name }}（{{ currentEmployee.employee_no }}）- {{ queryMonth }} 日工时明细</span>
          <el-button size="small" @click="currentEmployee = null">关闭明细</el-button>
        </div>
      </template>
      <el-table :data="currentEmployee.days" stripe size="small">
        <el-table-column prop="date" label="日期" width="110" />
        <el-table-column prop="weekday" label="星期" width="70" />
        <el-table-column prop="shift" label="班次" width="100" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.status==='请假'" size="small" type="info">请假</el-tag>
            <el-tag v-else-if="row.status==='加班'" size="small" type="warning">加班</el-tag>
            <el-tag v-else size="small" type="success">正常</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="regular_hours" label="正常工时" width="100">
          <template #default="{ row }">{{ row.regular_hours }}h</template>
        </el-table-column>
        <el-table-column prop="overtime_hours" label="加班工时" width="100">
          <template #default="{ row }"><span style="color:#ec6921">{{ row.overtime_hours }}h</span></template>
        </el-table-column>
        <el-table-column prop="leave_hours" label="请假工时" width="100">
          <template #default="{ row }">{{ row.leave_hours }}h</template>
        </el-table-column>
        <el-table-column prop="total" label="合计" width="80">
          <template #default="{ row }"><b>{{ row.total }}h</b></template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-empty v-if="!loading && summary.length === 0" description="暂无报表数据" style="margin-top:60px" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { get } from '@/api/request'
import * as XLSX from 'xlsx'

const queryMonth = ref(new Date().getFullYear() + '-' + String(new Date().getMonth()+1).padStart(2,'0'))
const queryType = ref('')
const queryDept = ref('')
const keyword = ref('')
const loading = ref(false)
const exporting = ref(false)
const summary = ref([])
const departments = ref([])
const currentEmployee = ref(null)

const monthOptions = computed(() => {
  const opts = []
  const now = new Date()
  for (let i = 0; i < 6; i++) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    opts.push(d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0'))
  }
  return opts
})

const loadReport = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({ month: queryMonth.value })
    const res = await get(`/api/work-hours/daily-report?${params.toString()}`)
    let list = res.employees || []
    if (queryType.value) list = list.filter(e => e.employee_type === queryType.value)
    if (keyword.value) list = list.filter(e => e.name.includes(keyword.value) || e.employee_no.includes(keyword.value))

    // 按类型分别汇总
    summary.value = list.map(e => ({
      ...e,
      regular_hours: e.summary?.regular_hours || 0,
      overtime_hours: e.summary?.overtime_hours || 0,
      leave_hours: e.summary?.leave_hours || 0,
      total_hours: e.summary?.total_hours || 0
    }))

    departments.value = [...new Set(summary.value.map(e => e.employee_no))]
  } catch(e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const showDetail = (row) => {
  currentEmployee.value = summary.value.find(e => e.employee_no === row.employee_no)
}

const exportExcel = async () => {
  exporting.value = true
  try {
    const wb = XLSX.utils.book_new()
    const data = summary.value.map(e => ({
      '工号': e.employee_no,
      '姓名': e.name,
      '员工类型': e.employee_type,
      '正常工时': e.regular_hours,
      '加班工时': e.overtime_hours,
      '请假工时': e.leave_hours,
      '合计工时': e.total_hours
    }))
    const ws = XLSX.utils.json_to_sheet(data)
    XLSX.utils.book_append_sheet(wb, ws, '月工时汇总')
    XLSX.writeFile(wb, `工时报表_${queryMonth.value}.xlsx`)
    ElMessage.success('导出成功')
  } catch(e) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

onMounted(loadReport)
</script>

<style scoped>
.report-page { padding: 24px; }
.page-header { margin-bottom: 20px; }
.page-header h2 { margin: 0 0 4px; font-size: 18px; color: #333; }
.subtitle { margin: 0; font-size: 13px; color: #999; }
.filter-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
</style>
