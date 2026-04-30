<template>
  <div class="settings-page">
    <el-row :gutter="16">
      <!-- 公司信息设置 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><OfficeBuilding /></el-icon>
              <span>公司信息</span>
            </div>
          </template>
          <el-form :model="companyForm" label-width="100px">
            <el-form-item label="公司名称">
              <el-input v-model="companyForm.name" placeholder="请输入公司名称" />
            </el-form-item>
            <el-form-item label="公司简称">
              <el-input v-model="companyForm.short_name" placeholder="请输入公司简称" />
            </el-form-item>
            <el-form-item label="统一社会信用代码">
              <el-input v-model="companyForm.credit_code" placeholder="请输入统一社会信用代码" />
            </el-form-item>
            <el-form-item label="公司地址">
              <el-input v-model="companyForm.address" type="textarea" :rows="2" placeholder="请输入公司地址" />
            </el-form-item>
            <el-form-item label="联系电话">
              <el-input v-model="companyForm.phone" placeholder="请输入联系电话" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveCompany" style="background:#ec6921;border-color:#ec6921;">
                保存
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 考勤规则设置 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><Clock /></el-icon>
              <span>考勤规则</span>
            </div>
          </template>
          <el-form :model="attendanceForm" label-width="120px">
            <el-form-item label="上班时间">
              <el-time-picker
                v-model="attendanceForm.work_start_time"
                format="HH:mm"
                value-format="HH:mm"
                placeholder="选择上班时间"
                style="width:100%"
              />
            </el-form-item>
            <el-form-item label="下班时间">
              <el-time-picker
                v-model="attendanceForm.work_end_time"
                format="HH:mm"
                value-format="HH:mm"
                placeholder="选择下班时间"
                style="width:100%"
              />
            </el-form-item>
            <el-form-item label="迟到容忍(分钟)">
              <el-input-number v-model="attendanceForm.late_tolerance" :min="0" :max="60" style="width:100%" />
            </el-form-item>
            <el-form-item label="早退容忍(分钟)">
              <el-input-number v-model="attendanceForm.early_tolerance" :min="0" :max="60" style="width:100%" />
            </el-form-item>
            <el-form-item label="工作日">
              <el-checkbox-group v-model="attendanceForm.work_days">
                <el-checkbox label="1">周一</el-checkbox>
                <el-checkbox label="2">周二</el-checkbox>
                <el-checkbox label="3">周三</el-checkbox>
                <el-checkbox label="4">周四</el-checkbox>
                <el-checkbox label="5">周五</el-checkbox>
                <el-checkbox label="6">周六</el-checkbox>
                <el-checkbox label="0">周日</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveAttendance" style="background:#ec6921;border-color:#ec6921;">
                保存
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px;">
      <!-- 假期设置 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><Calendar /></el-icon>
              <span>假期设置</span>
            </div>
          </template>
          <el-form :model="leaveForm" label-width="120px">
            <el-form-item label="年假天数">
              <el-input-number v-model="leaveForm.annual_leave_days" :min="0" :max="30" style="width:100%" />
            </el-form-item>
            <el-form-item label="病假天数">
              <el-input-number v-model="leaveForm.sick_leave_days" :min="0" :max="30" style="width:100%" />
            </el-form-item>
            <el-form-item label="事假天数">
              <el-input-number v-model="leaveForm.personal_leave_days" :min="0" :max="30" style="width:100%" />
            </el-form-item>
            <el-form-item label="调休天数">
              <el-input-number v-model="leaveForm.compensatory_leave_days" :min="0" :max="30" style="width:100%" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveLeave" style="background:#ec6921;border-color:#ec6921;">
                保存
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 系统设置 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><Setting /></el-icon>
              <span>系统设置</span>
            </div>
          </template>
          <el-form :model="systemForm" label-width="120px">
            <el-form-item label="系统名称">
              <el-input v-model="systemForm.system_name" placeholder="请输入系统名称" />
            </el-form-item>
            <el-form-item label="登录有效期">
              <el-select v-model="systemForm.session_timeout" style="width:100%">
                <el-option label="30分钟" value="30" />
                <el-option label="1小时" value="60" />
                <el-option label="2小时" value="120" />
                <el-option label="4小时" value="240" />
                <el-option label="8小时" value="480" />
              </el-select>
            </el-form-item>
            <el-form-item label="数据备份">
              <el-switch v-model="systemForm.auto_backup" active-text="开启自动备份" />
            </el-form-item>
            <el-form-item label="备份周期">
              <el-select v-model="systemForm.backup_interval" style="width:100%" :disabled="!systemForm.auto_backup">
                <el-option label="每天" value="daily" />
                <el-option label="每周" value="weekly" />
                <el-option label="每月" value="monthly" />
              </el-select>
            </el-form-item>
            <el-form-item label="系统主题">
              <el-radio-group v-model="systemForm.theme">
                <el-radio label="light">浅色</el-radio>
                <el-radio label="dark">深色</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSystem" style="background:#ec6921;border-color:#ec6921;">
                保存
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <!-- 操作日志 -->
    <el-row style="margin-top:16px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>操作日志</span>
            </div>
          </template>
          <el-table :data="logs" style="width:100%" border>
            <el-table-column prop="time" label="时间" width="180" />
            <el-table-column prop="user" label="操作人" width="120" />
            <el-table-column prop="action" label="操作类型" width="120">
              <template #default="scope">
                <el-tag :type="getLogTagType(scope.row.action)" size="small">{{ scope.row.action }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="detail" label="操作详情" />
            <el-table-column prop="ip" label="IP地址" width="140" />
          </el-table>
          <el-pagination
            v-model:current-page="logPage"
            v-model:page-size="logPageSize"
            :total="logTotal"
            layout="total, prev, pager, next"
            style="margin-top:16px;justify-content:flex-end;"
            @current-change="fetchLogs"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { OfficeBuilding, Clock, Calendar, Setting, Document } from '@element-plus/icons-vue'
import { getCompanyInfo, saveCompanyInfo, getAttendanceRule, saveAttendanceRule, getLeaveRule, saveLeaveRule, getSystemConfig, saveSystemConfig, getLogs } from '@/api/settings'

const companyForm = reactive({
  name: '海昌新材',
  short_name: '海昌新材',
  credit_code: '',
  address: '',
  phone: ''
})

const attendanceForm = reactive({
  work_start_time: '08:30',
  work_end_time: '17:30',
  late_tolerance: 5,
  early_tolerance: 5,
  work_days: ['1', '2', '3', '4', '5']
})

const leaveForm = reactive({
  annual_leave_days: 5,
  sick_leave_days: 10,
  personal_leave_days: 5,
  compensatory_leave_days: 0
})

const systemForm = reactive({
  system_name: '海昌新材人事考勤系统',
  session_timeout: '120',
  auto_backup: true,
  backup_interval: 'daily',
  theme: 'light'
})

const logs = ref([])
const logPage = ref(1)
const logPageSize = ref(10)
const logTotal = ref(0)

const getLogTagType = (action) => {
  const map = {
    '登录': 'success',
    '登出': 'info',
    '新增': 'success',
    '修改': 'warning',
    '删除': 'danger',
    '导出': 'primary'
  }
  return map[action] || 'info'
}

const saveCompany = async () => {
  try {
    await saveCompanyInfo(companyForm)
    ElMessage.success('公司信息保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const saveAttendance = async () => {
  try {
    await saveAttendanceRule(attendanceForm)
    ElMessage.success('考勤规则保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const saveLeave = async () => {
  try {
    await saveLeaveRule(leaveForm)
    ElMessage.success('假期设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const saveSystem = async () => {
  try {
    await saveSystemConfig(systemForm)
    ElMessage.success('系统设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const fetchLogs = async () => {
  try {
    const res = await getLogs({ page: logPage.value, page_size: logPageSize.value })
    logs.value = res.items.map(item => ({
      time: item.created_at,
      user: item.username || '系统',
      action: item.action,
      detail: item.detail,
      ip: item.ip_address || '-'
    }))
    logTotal.value = res.total
  } catch (error) {
    console.error('获取日志失败', error)
  }
}

onMounted(async () => {
  try {
    const company = await getCompanyInfo()
    Object.assign(companyForm, company)
    const attendance = await getAttendanceRule()
    Object.assign(attendanceForm, attendance)
    const leave = await getLeaveRule()
    Object.assign(leaveForm, leave)
    const system = await getSystemConfig()
    Object.assign(systemForm, system)
  } catch (error) {
    console.error('加载设置失败', error)
  }
  fetchLogs()
})
</script>

<style scoped>
.settings-page { padding: 0; }
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}
</style>
