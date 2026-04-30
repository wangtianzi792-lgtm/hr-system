<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-icon" style="background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_employees || 0 }}</div>
              <div class="stat-label">总员工数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-icon" style="background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);">
              <el-icon><Check /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.today_punched || 0 }}</div>
              <div class="stat-label">今日出勤</div>
              <div class="stat-rate" v-if="stats.attendance_rate">{{ stats.attendance_rate }}%</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-icon" style="background: linear-gradient(135deg, #E6A23C 0%, #ebb563 100%);">
              <el-icon><WarningFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.today_late || 0 }}</div>
              <div class="stat-label">迟到人数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-icon" style="background: linear-gradient(135deg, #F56C6C 0%, #f78989 100%);">
              <el-icon><CircleCloseFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.today_absent || 0 }}</div>
              <div class="stat-label">缺勤人数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>本周出勤趋势</span>
              <el-tag size="small" type="info">最近7天</el-tag>
            </div>
          </template>
          <div ref="weekChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>部门出勤统计</span>
              <el-tag size="small" type="info">今日</el-tag>
            </div>
          </template>
          <div ref="deptChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近考勤记录 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>最近考勤记录</span>
          <el-button type="primary" link @click="$router.push('/attendance')">
            查看更多 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>
      <el-table :data="recentRecords" style="width: 100%" v-loading="loading">
        <el-table-column prop="employee_name" label="员工姓名" min-width="100" />
        <el-table-column prop="department" label="部门" min-width="120" />
        <el-table-column prop="punch_time" label="打卡时间" min-width="160" />
        <el-table-column prop="status_text" label="状态" min-width="80">
          <template #default="scope">
            <el-tag :type="scope.row.tag_type" size="small">
              {{ scope.row.status_text }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getDashboardStats, getWeekTrend, getDeptStats, getRecentRecords } from '@/api/dashboard'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const stats = reactive({
  total_employees: 0,
  today_punched: 0,
  today_late: 0,
  today_absent: 0,
  attendance_rate: 0,
  pending_leaves: 0
})

const recentRecords = ref([])
const weekChartRef = ref(null)
const deptChartRef = ref(null)

let weekChart = null
let deptChart = null

// 获取统计数据
const fetchStats = async () => {
  try {
    const res = await getDashboardStats()
    Object.assign(stats, res)
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 获取最近记录
const fetchRecentRecords = async () => {
  loading.value = true
  try {
    const res = await getRecentRecords(10)
    recentRecords.value = res
  } catch (error) {
    console.error('获取最近记录失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取本周趋势并渲染图表
const fetchWeekTrend = async () => {
  try {
    const data = await getWeekTrend()
    const dates = data.map(item => item.date)
    const counts = data.map(item => item.count)
    
    weekChart = echarts.init(weekChartRef.value)
    weekChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: dates },
      yAxis: { type: 'value', minInterval: 1 },
      series: [{
        data: counts,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { color: '#ec6921', width: 3 },
        itemStyle: { color: '#ec6921' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(236, 105, 33, 0.3)' },
              { offset: 1, color: 'rgba(236, 105, 33, 0.05)' }
            ]
          }
        }
      }]
    })
  } catch (error) {
    console.error('获取趋势数据失败:', error)
  }
}

// 获取部门统计并渲染图表
const fetchDeptStats = async () => {
  try {
    const data = await getDeptStats()
    const names = data.map(item => item.dept_name)
    const rates = data.map(item => item.rate)
    
    deptChart = echarts.init(deptChartRef.value)
    deptChart.setOption({
      tooltip: { trigger: 'axis', formatter: '{b}: {c}%' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
      yAxis: { type: 'category', data: names },
      series: [{
        data: rates,
        type: 'bar',
        barWidth: '60%',
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [
              { offset: 0, color: '#ec6921' },
              { offset: 1, color: '#f0884a' }
            ]
          },
          borderRadius: [0, 4, 4, 0]
        },
        label: { show: true, position: 'right', formatter: '{c}%' }
      }]
    })
  } catch (error) {
    console.error('获取部门统计失败:', error)
  }
}

// 窗口大小变化时重绘图表
const handleResize = () => {
  weekChart && weekChart.resize()
  deptChart && deptChart.resize()
}

onMounted(() => {
  fetchStats()
  fetchRecentRecords()
  nextTick(() => {
    fetchWeekTrend()
    fetchDeptStats()
  })
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-item {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
  margin-right: 16px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.stat-rate {
  font-size: 12px;
  color: #67C23A;
  margin-top: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
