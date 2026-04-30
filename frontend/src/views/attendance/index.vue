<template>
  <div class="attendance-page">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
            @change="handleSearch"
          />
        </el-col>
        <el-col :span="5">
          <el-select v-model="filterEmployee" placeholder="选择员工" clearable @change="handleSearch">
            <el-option
              v-for="emp in employeeList"
              :key="emp.id"
              :label="emp.name"
              :value="emp.id"
            />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="filterStatus" placeholder="考勤状态" clearable @change="handleSearch">
            <el-option label="正常" value="normal" />
            <el-option label="迟到" value="late" />
            <el-option label="早退" value="early" />
            <el-option label="异常" value="exception" />
          </el-select>
        </el-col>
        <el-col :span="8" style="text-align: right;">
          <el-button type="primary" @click="handleSearch" style="background-color: #ec6921; border-color: #ec6921;">
            <el-icon><Search /></el-icon>查询
          </el-button>
          <el-button @click="handleReset" style="color: #ec6921; border-color: #ec6921;">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
          <el-button type="success" @click="handleCollect" style="background-color: #67C23A; border-color: #67C23A;">
            <el-icon><Download /></el-icon>采集数据
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="4">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ statistics.total }}</div>
            <div class="stat-label">总记录</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-item">
            <div class="stat-value" style="color: #67C23A;">{{ statistics.normal }}</div>
            <div class="stat-label">正常</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-item">
            <div class="stat-value" style="color: #E6A23C;">{{ statistics.late }}</div>
            <div class="stat-label">迟到</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-item">
            <div class="stat-value" style="color: #F56C6C;">{{ statistics.early }}</div>
            <div class="stat-label">早退</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-item">
            <div class="stat-value" style="color: #909399;">{{ statistics.exception }}</div>
            <div class="stat-label">异常</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-item">
            <div class="stat-value" style="color: #409EFF;">{{ statistics.leave }}</div>
            <div class="stat-label">请假</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 考勤记录列表 -->
    <el-card style="margin-top: 20px;">
      <el-table :data="attendanceList" v-loading="loading" style="width: 100%">
        <el-table-column prop="employee_name" label="员工姓名" width="100" />
        <el-table-column prop="employee_no" label="工号" width="100">
          <template #default="scope">
            {{ scope.row.employee?.employee_no || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="department_name" label="部门" width="120">
          <template #default="scope">
            {{ scope.row.employee?.department?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="punch_date" label="日期" width="110" />
        <el-table-column prop="punch_time" label="打卡时间" width="160" />
        <el-table-column prop="punch_type" label="类型" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.punch_type === 'check_in' ? 'primary' : 'info'" size="small">
              {{ scope.row.punch_type === 'check_in' ? '上班' : '下班' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="verify_type" label="验证方式" width="100">
          <template #default="scope">
            {{ getVerifyTypeText(scope.row.verify_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="device_name" label="考勤机" min-width="120">
          <template #default="scope">
            {{ scope.row.device?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewDetail(scope.row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        style="margin-top: 20px; justify-content: flex-end;"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="考勤详情" width="500px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="员工姓名">{{ currentRecord?.employee_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="工号">{{ currentRecord?.employee?.employee_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="部门">{{ currentRecord?.employee?.department?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="打卡日期">{{ currentRecord?.punch_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="打卡时间">{{ currentRecord?.punch_time || '-' }}</el-descriptions-item>
        <el-descriptions-item label="打卡类型">{{ currentRecord?.punch_type === 'check_in' ? '上班' : '下班' }}</el-descriptions-item>
        <el-descriptions-item label="验证方式">{{ getVerifyTypeText(currentRecord?.verify_type) }}</el-descriptions-item>
        <el-descriptions-item label="考勤机">{{ currentRecord?.device?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentRecord?.status)" size="small">
            {{ getStatusText(currentRecord?.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="原始数据">{{ currentRecord?.raw_data || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 采集数据对话框 -->
    <el-dialog v-model="collectVisible" title="采集考勤数据" width="400px">
      <p>将从考勤机同步最新打卡记录到系统。</p>
      <el-form label-width="100px">
        <el-form-item label="选择设备">
          <el-select v-model="selectedDevice" placeholder="全部设备" clearable style="width: 100%">
            <el-option label="全部设备" value="" />
            <el-option
              v-for="device in deviceList"
              :key="device.id"
              :label="device.name"
              :value="device.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="collectVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmCollect" :loading="collectLoading" style="background-color: #ec6921; border-color: #ec6921;">
          开始采集
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAttendanceRecords, collectAttendance } from '@/api/attendance'
import { getEmployees } from '@/api/employees'
import { getDevices } from '@/api/devices'

// 数据
const attendanceList = ref([])
const employeeList = ref([])
const deviceList = ref([])
const loading = ref(false)
const dateRange = ref([])
const filterEmployee = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const statistics = reactive({
  total: 0,
  normal: 0,
  late: 0,
  early: 0,
  exception: 0,
  leave: 0
})

// 详情对话框
const detailVisible = ref(false)
const currentRecord = ref(null)

// 采集对话框
const collectVisible = ref(false)
const collectLoading = ref(false)
const selectedDevice = ref('')

// 获取考勤记录
const fetchAttendance = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      ...(filterEmployee.value && { employee_id: filterEmployee.value }),
      ...(filterStatus.value && { status: filterStatus.value }),
      ...(dateRange.value?.[0] && { start_date: dateRange.value[0] }),
      ...(dateRange.value?.[1] && { end_date: dateRange.value[1] })
    }
    const res = await getAttendanceRecords(params)
    attendanceList.value = res.items || []
    total.value = res.total || 0
    
    // 计算统计
    calculateStats(res.items || [])
  } catch (error) {
    console.error('获取考勤记录失败:', error)
    ElMessage.error('获取考勤记录失败')
  } finally {
    loading.value = false
  }
}

// 计算统计
const calculateStats = (items) => {
  const stats = { total: items.length, normal: 0, late: 0, early: 0, exception: 0, leave: 0 }
  items.forEach(item => {
    if (item.status === 'normal') stats.normal++
    else if (item.status === 'late') stats.late++
    else if (item.status === 'early') stats.early++
    else if (item.status === 'exception') stats.exception++
    else if (item.status === 'leave') stats.leave++
  })
  Object.assign(statistics, stats)
}

// 获取员工列表
const fetchEmployees = async () => {
  try {
    const res = await getEmployees({ limit: 1000 })
    employeeList.value = res.items || []
  } catch (error) {
    console.error('获取员工列表失败:', error)
  }
}

// 获取设备列表
const fetchDevices = async () => {
  try {
    const res = await getDevices({ limit: 100 })
    deviceList.value = res.items || []
  } catch (error) {
    console.error('获取设备列表失败:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchAttendance()
}

const handleReset = () => {
  dateRange.value = []
  filterEmployee.value = ''
  filterStatus.value = ''
  currentPage.value = 1
  fetchAttendance()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchAttendance()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchAttendance()
}

const handleCollect = () => {
  selectedDevice.value = ''
  collectVisible.value = true
}

const confirmCollect = async () => {
  collectLoading.value = true
  try {
    const res = await collectAttendance(selectedDevice.value || null)
    ElMessage.success(res.message || '采集完成')
    collectVisible.value = false
    fetchAttendance()
  } catch (error) {
    console.error('采集失败:', error)
    ElMessage.error('采集失败')
  } finally {
    collectLoading.value = false
  }
}

const viewDetail = (row) => {
  currentRecord.value = row
  detailVisible.value = true
}

const getStatusType = (status) => {
  const types = { normal: 'success', late: 'warning', early: 'warning', exception: 'danger', leave: 'info' }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = { normal: '正常', late: '迟到', early: '早退', exception: '异常', leave: '请假' }
  return texts[status] || status
}

const getVerifyTypeText = (type) => {
  const texts = ['指纹', '面部', '密码', '卡', '混合']
  return texts[type] || '其他'
}

onMounted(() => {
  fetchAttendance()
  fetchEmployees()
  fetchDevices()
})
</script>

<style scoped>
.attendance-page {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
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
