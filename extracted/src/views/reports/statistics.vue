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
            @change="fetchData"
          />
        </el-col>
        <el-col :span="18" style="text-align: right;">
          <el-button type="primary" @click="fetchData" style="background:#ec6921;border-color:#ec6921;">
            <el-icon><Search /></el-icon>查询
          </el-button>
          <el-button @click="resetFilters"><el-icon><Refresh /></el-icon>重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="16" style="margin-top:16px;">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value" style="color:#409EFF;">{{ stats.total_employees }}</div>
          <div class="stat-label">总人数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value" style="color:#67C23A;">{{ stats.avg_attendance_rate }}%</div>
          <div class="stat-label">平均出勤率</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value" style="color:#E6A23C;">{{ stats.total_late }}</div>
          <div class="stat-label">总迟到次数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value" style="color:#F56C6C;">{{ stats.total_early }}</div>
          <div class="stat-label">总早退次数</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>部门出勤率排行</span>
          </template>
          <div v-for="(dept, index) in deptRanking" :key="index" class="ranking-item">
            <div class="ranking-info">
              <span class="ranking-num" :class="{ top3: index < 3 }">{{ index + 1 }}</span>
              <span class="ranking-name">{{ dept.name }}</span>
            </div>
            <el-progress :percentage="dept.rate" :color="getProgressColor(dept.rate)" style="flex:1;margin:0 12px;" />
            <span class="ranking-value">{{ dept.rate }}%</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>考勤异常统计</span>
          </template>
          <el-table :data="abnormalStats" style="width:100%" border>
            <el-table-column prop="type" label="异常类型" />
            <el-table-column prop="count" label="次数" align="center" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.tagType" size="small">{{ scope.row.count }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="percentage" label="占比" align="center" width="100">
              <template #default="scope">
                {{ scope.row.percentage }}%
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAttendanceReport } from '@/api/attendance'
import { getDepartments } from '@/api/departments'

const loading = ref(false)
const dateRange = ref([])
const stats = reactive({
  total_employees: 0,
  avg_attendance_rate: 0,
  total_late: 0,
  total_early: 0
})
const deptRanking = ref([])
const abnormalStats = ref([])

const getProgressColor = (rate) => {
  if (rate >= 95) return '#67C23A'
  if (rate >= 80) return '#E6A23C'
  return '#F56C6C'
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      start_date: dateRange.value && dateRange.value[0] ? dateRange.value[0] : getDefaultStartDate(),
      end_date: dateRange.value && dateRange.value[1] ? dateRange.value[1] : getDefaultEndDate(),
      limit: 1000
    }

    const [reportRes, deptRes] = await Promise.all([
      getAttendanceReport(params),
      getDepartments({ limit: 100 })
    ])

    const data = reportRes.items || []
    const departments = Array.isArray(deptRes) ? deptRes : (deptRes.items || [])

    // 基础统计
    stats.total_employees = data.length
    stats.total_late = data.reduce((s, r) => s + (r.late_count || 0), 0)
    stats.total_early = data.reduce((s, r) => s + (r.early_count || 0), 0)
    const totalWorkDays = data.reduce((s, r) => s + (r.work_days || 0), 0)
    const totalActualDays = data.reduce((s, r) => s + (r.actual_days || 0), 0)
    stats.avg_attendance_rate = totalWorkDays > 0 ? Math.round((totalActualDays / totalWorkDays) * 100) : 0

    // 部门排行
    const deptMap = {}
    data.forEach(item => {
      const deptId = item.department_id || 0
      if (!deptMap[deptId]) {
        deptMap[deptId] = { name: item.department_name || '未分配', work_days: 0, actual_days: 0 }
      }
      deptMap[deptId].work_days += (item.work_days || 0)
      deptMap[deptId].actual_days += (item.actual_days || 0)
    })

    deptRanking.value = Object.values(deptMap)
      .map(d => ({
        name: d.name,
        rate: d.work_days > 0 ? Math.round((d.actual_days / d.work_days) * 100) : 0
      }))
      .sort((a, b) => b.rate - a.rate)

    // 异常统计
    const totalAbnormal = stats.total_late + stats.total_early + data.reduce((s, r) => s + (r.absent_days || 0), 0)
    abnormalStats.value = [
      { type: '迟到', count: stats.total_late, percentage: totalAbnormal > 0 ? Math.round((stats.total_late / totalAbnormal) * 100) : 0, tagType: 'warning' },
      { type: '早退', count: stats.total_early, percentage: totalAbnormal > 0 ? Math.round((stats.total_early / totalAbnormal) * 100) : 0, tagType: 'danger' },
      { type: '缺勤', count: data.reduce((s, r) => s + (r.absent_days || 0), 0), percentage: totalAbnormal > 0 ? Math.round((data.reduce((s, r) => s + (r.absent_days || 0), 0) / totalAbnormal) * 100) : 0, tagType: 'info' }
    ]
  } catch (e) {
    console.error('加载统计失败', e)
    ElMessage.error('加载统计失败')
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
  dateRange.value = [getDefaultStartDate(), getDefaultEndDate()]
  fetchData()
}

onMounted(() => {
  dateRange.value = [getDefaultStartDate(), getDefaultEndDate()]
  fetchData()
})
</script>

<style scoped>
.reports-page { padding: 0; }
.search-card { margin-bottom: 0; }
.stat-card { text-align: center; padding: 8px 0; }
.stat-value { font-size: 24px; font-weight: 700; line-height: 1.2; }
.stat-label { font-size: 12px; color: #999; margin-top: 4px; }
.ranking-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}
.ranking-item:last-child { border-bottom: none; }
.ranking-info { display: flex; align-items: center; width: 120px; }
.ranking-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #f0f0f0;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  margin-right: 8px;
}
.ranking-num.top3 { background: #ec6921; color: #fff; }
.ranking-name { font-size: 14px; color: #333; }
.ranking-value { font-size: 14px; font-weight: 600; color: #666; width: 50px; text-align: right; }
</style>
