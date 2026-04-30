<template>
  <div class="approval-page">
    <el-tabs v-model="activeTab" type="border-card" @tab-change="handleTabChange">
      <el-tab-pane label="请假审批" name="leave">
        <el-card class="search-card">
          <el-row :gutter="20" align="middle">
            <el-col :span="6">
              <el-select v-model="leaveFilters.leave_type" placeholder="请假类型" clearable style="width:100%" @change="fetchLeaveData">
                <el-option label="年假" value="年假" />
                <el-option label="病假" value="病假" />
                <el-option label="事假" value="事假" />
                <el-option label="婚假" value="婚假" />
                <el-option label="产假" value="产假" />
                <el-option label="丧假" value="丧假" />
                <el-option label="调休" value="调休" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="leaveFilters.status" placeholder="审批状态" clearable style="width:100%" @change="fetchLeaveData">
                <el-option label="待审批" value="pending" />
                <el-option label="已通过" value="approved" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
            </el-col>
            <el-col :span="8">
              <el-date-picker
                v-model="leaveFilters.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width:100%"
                @change="fetchLeaveData"
              />
            </el-col>
            <el-col :span="4" style="text-align: right;">
              <el-button @click="fetchLeaveData"><el-icon><Refresh /></el-icon>刷新</el-button>
            </el-col>
          </el-row>
        </el-card>

        <el-card style="margin-top:16px;">
          <el-table :data="leaveList" v-loading="loading" style="width:100%">
            <el-table-column prop="employee_name" label="员工姓名" width="120" />
            <el-table-column prop="employee_no" label="工号" width="100" />
            <el-table-column prop="department_name" label="部门" width="120" />
            <el-table-column prop="leave_type" label="请假类型" width="100">
              <template #default="scope">
                <el-tag size="small">{{ scope.row.leave_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="请假日期" width="200">
              <template #default="scope">
                {{ scope.row.start_date }} ~ {{ scope.row.end_date }}
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
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="scope">
                <el-button v-if="scope.row.status === 'pending'" size="small" type="success" @click="handleApprove(scope.row, true, false)">通过</el-button>
                <el-button v-if="scope.row.status === 'pending'" size="small" type="danger" @click="handleApprove(scope.row, false, false)">拒绝</el-button>
                <span v-else style="color:#999;">已处理</span>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="leavePage.current" v-model:page-size="leavePage.size"
            :total="leavePage.total" :page-sizes="[10,20,50]"
            layout="total,sizes,prev,pager,next"
            style="margin-top:16px;justify-content:flex-end;"
            @size-change="fetchLeaveData" @current-change="fetchLeaveData"
          />
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="加班审批" name="overtime">
        <el-card class="search-card">
          <el-row :gutter="20" align="middle">
            <el-col :span="6">
              <el-select v-model="overtimeFilters.status" placeholder="审批状态" clearable style="width:100%" @change="fetchOvertimeData">
                <el-option label="待审批" value="pending" />
                <el-option label="已通过" value="approved" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
            </el-col>
            <el-col :span="12">
              <el-date-picker
                v-model="overtimeFilters.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width:100%"
                @change="fetchOvertimeData"
              />
            </el-col>
            <el-col :span="6" style="text-align: right;">
              <el-button @click="fetchOvertimeData"><el-icon><Refresh /></el-icon>刷新</el-button>
            </el-col>
          </el-row>
        </el-card>

        <el-card style="margin-top:16px;">
          <el-table :data="overtimeList" v-loading="loading" style="width:100%">
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
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="scope">
                <el-button v-if="scope.row.status === 'pending'" size="small" type="success" @click="handleApprove(scope.row, true, true)">通过</el-button>
                <el-button v-if="scope.row.status === 'pending'" size="small" type="danger" @click="handleApprove(scope.row, false, true)">拒绝</el-button>
                <span v-else style="color:#999;">已处理</span>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="overtimePage.current" v-model:page-size="overtimePage.size"
            :total="overtimePage.total" :page-sizes="[10,20,50]"
            layout="total,sizes,prev,pager,next"
            style="margin-top:16px;justify-content:flex-end;"
            @size-change="fetchOvertimeData" @current-change="fetchOvertimeData"
          />
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 审批对话框 -->
    <el-dialog v-model="approveDialogVisible" title="审批" width="400px">
      <p>确定{{ approveAction ? '通过' : '拒绝' }}该申请？</p>
      <el-input v-model="approveComment" type="textarea" :rows="2" placeholder="审批意见（可选）" style="margin-top:12px;" />
      <template #footer>
        <el-button @click="approveDialogVisible=false">取消</el-button>
        <el-button type="primary" @click="submitApprove" :loading="submitLoading" style="background:#ec6921;border-color:#ec6921;">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getLeaveRequests, approveLeaveRequest } from '@/api/leave'
import { getOvertimeRequests, approveOvertimeRequest } from '@/api/leave'

const activeTab = ref('leave')
const loading = ref(false)
const submitLoading = ref(false)

const leaveList = ref([])
const overtimeList = ref([])

const leavePage = reactive({ current: 1, size: 20, total: 0 })
const overtimePage = reactive({ current: 1, size: 20, total: 0 })

const leaveFilters = reactive({ leave_type: '', status: 'pending', dateRange: [] })
const overtimeFilters = reactive({ status: 'pending', dateRange: [] })

const approveDialogVisible = ref(false)
const currentApproveItem = ref(null)
const approveAction = ref(true)
const approveComment = ref('')
const isOvertimeApprove = ref(false)

const statusMap = { pending: '待审批', approved: '已通过', rejected: '已拒绝' }

const fetchLeaveData = async () => {
  loading.value = true
  try {
    const params = { skip: (leavePage.current - 1) * leavePage.size, limit: leavePage.size }
    if (leaveFilters.leave_type) params.leave_type = leaveFilters.leave_type
    if (leaveFilters.status) params.status = leaveFilters.status
    if (leaveFilters.dateRange && leaveFilters.dateRange.length === 2) {
      params.start_date = leaveFilters.dateRange[0]
      params.end_date = leaveFilters.dateRange[1]
    }
    const res = await getLeaveRequests(params)
    const data = Array.isArray(res) ? res : (res.items || [])
    leaveList.value = data
    leavePage.total = Array.isArray(res) ? res.length : (res.total || data.length)
  } catch (e) {
    ElMessage.error('加载请假记录失败')
  } finally {
    loading.value = false
  }
}

const fetchOvertimeData = async () => {
  loading.value = true
  try {
    const params = { skip: (overtimePage.current - 1) * overtimePage.size, limit: overtimePage.size }
    if (overtimeFilters.status) params.status = overtimeFilters.status
    if (overtimeFilters.dateRange && overtimeFilters.dateRange.length === 2) {
      params.start_date = overtimeFilters.dateRange[0]
      params.end_date = overtimeFilters.dateRange[1]
    }
    const res = await getOvertimeRequests(params)
    const data = Array.isArray(res) ? res : (res.items || [])
    overtimeList.value = data
    overtimePage.total = Array.isArray(res) ? res.length : (res.total || data.length)
  } catch (e) {
    ElMessage.error('加载加班记录失败')
  } finally {
    loading.value = false
  }
}

const handleApprove = (row, approved, isOvertime) => {
  currentApproveItem.value = row
  approveAction.value = approved
  isOvertimeApprove.value = isOvertime
  approveComment.value = ''
  approveDialogVisible.value = true
}

const submitApprove = async () => {
  submitLoading.value = true
  try {
    if (isOvertimeApprove.value) {
      await approveOvertimeRequest(currentApproveItem.value.id, approveAction.value, approveComment.value)
    } else {
      await approveLeaveRequest(currentApproveItem.value.id, approveAction.value, approveComment.value)
    }
    ElMessage.success(approveAction.value ? '审批通过' : '已拒绝')
    approveDialogVisible.value = false
    if (isOvertimeApprove.value) {
      fetchOvertimeData()
    } else {
      fetchLeaveData()
    }
  } catch (e) {
    ElMessage.error('审批失败')
  } finally {
    submitLoading.value = false
  }
}

const handleTabChange = () => {
  if (activeTab.value === 'leave') {
    fetchLeaveData()
  } else {
    fetchOvertimeData()
  }
}

onMounted(() => { fetchLeaveData() })
</script>

<style scoped>
.approval-page { padding: 0; }
.search-card { margin-bottom: 0; }
</style>
