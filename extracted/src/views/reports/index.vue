<template>
  <div class="reports-page">
    <!-- 筛选条件 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-date-picker
            v-model="dateRange"
            type="monthrange"
            range-separator="至"
            start-placeholder="开始月份"
            end-placeholder="结束月份"
            style="width: 100%"
          />
        </el-col>
        <el-col :span="6">
          <el-select v-model="filterDepartment" placeholder="选择部门" clearable>
            <el-option
              v-for="dept in departmentList"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="reportType" placeholder="报表类型">
            <el-option label="日报" value="daily" />
            <el-option label="月报" value="monthly" />
            <el-option label="部门统计" value="department" />
          </el-select>
        </el-col>
        <el-col :span="6" style="text-align: right;">
          <el-button type="primary" @click="generateReport" style="background-color: #ec6921; border-color: #ec6921;">
            <el-icon><Search /></el-icon>生成报表
          </el-button>
          <el-button @click="handleExport" style="color: #ec6921; border-color: #ec6921;">
            <el-icon><Download /></el-icon>导出Excel
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计概览 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-icon" style="background: #409EFF;">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ summary.totalEmployees }}</div>
              <div class="stat-label">应到人数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-icon" style="background: #67C23A;">
              <el-icon><Check /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ summary.avgAttendanceRate }}%</div>
              <div class="stat-label">平均出勤率</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-icon" style="background: #E6A23C;">
              <el-icon><WarningFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ summary.totalLate }}</div>
              <div class="stat-label">迟到人次</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-icon" style="background: #F56C6C;">
              <el-icon><CircleCloseFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ summary.totalAbsent }}</div>
              <div class="stat-label">缺勤人次</div>
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
            <span>出勤趋势</span>
          </template>
          <div ref="trendChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>部门出勤对比</span>
          </template>
          <div ref="deptChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细报表 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>考勤明细报表</span>
      </template>
      <el-table :data="reportData" style="width: 100%">
        <el-table-column prop="employee_no" label="工号" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="department" label="部门" />
        <el-table-column prop="workDays" label="应出勤天数" />
        <el-table-column prop="actualDays" label="实际出勤" />
        <el-table-column prop="lateCount" label="迟到">
          <template #default="scope">
            <span style="color: #E6A23C;">{{ scope.row.lateCount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="earlyCount" label="早退">
          <template #default="scope">
            <span style="color: #E6A23C;">{{ scope.row.earlyCount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="absentCount" label="缺勤">
          <template #default="scope">
            <span style="color: #F56C6C;">{{ scope.row.absentCount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="leaveDays" label="请假">
          <template #default="scope">
            <span style="color: #409EFF;">{{ scope.row.leaveDays }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="attendanceRate" label="出勤率">
          <template #default="scope">
            <el-progress :percentage="scope.row.attendanceRate" :status="scope.row.attendanceRate >= 95 ? 'success' : 'warning'" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 数据
const dateRange = ref([])
const filterDepartment = ref('')
const reportType = ref('monthly')
const departmentList = ref([])
const reportData = ref([])

const summary = reactive({
  totalEmployees: 156,
  avgAttendanceRate: 94.5,
  totalLate: 23,
  totalAbsent: 12
})

// 方法
const fetchDepartments = async () => {
  // TODO: 调用 API
  departmentList.value = [
    { id: 1, name: '技术部' },
    { id: 2, name: '销售部' },
    { id: 3, name: '人事部' },
    { id: 4, name: '财务部' }
  ]
}

const generateReport = async () => {
  // TODO: 调用 API 生成报表
  reportData.value = [
    { employee_no: 'E001', name: '张三', department: '技术部', workDays: 22, actualDays: 21, lateCount: 1, earlyCount: 0, absentCount: 0, leaveDays: 1, attendanceRate: 95.5 },
    { employee_no: 'E002', name: '李四', department: '销售部', workDays: 22, actualDays: 20, lateCount: 2, earlyCount: 1, absentCount: 0, leaveDays: 1, attendanceRate: 90.9 },
    { employee_no: 'E003', name: '王五', department: '人事部', workDays: 22, actualDays: 22, lateCount: 0, earlyCount: 0, absentCount: 0, leaveDays: 0, attendanceRate: 100 }
  ]
  ElMessage.success('报表生成成功')
}

const handleExport = () => {
  ElMessage.success('导出功能开发中...')
}

onMounted(() => {
  fetchDepartments()
  generateReport()
})
</script>

<style scoped>
.reports-page {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #fff;
  margin-right: 15px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}
</style>
