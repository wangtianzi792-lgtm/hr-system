<template>
  <div class="adjustments-page">
    <div class="page-header">
      <h2>调休管理</h2>
      <p class="subtitle">员工换班/调休记录，审批通过后生效</p>
    </div>

    <el-card style="margin-bottom:16px">
      <template #header>
        <div class="card-header">
          <span>调休记录</span>
          <el-button type="primary" @click="openDialog()">
            <el-icon><Plus /></el-icon> 新增调休
          </el-button>
        </div>
      </template>

      <el-table :data="adjustments" stripe>
        <el-table-column prop="employee_no" label="工号" width="120" />
        <el-table-column prop="姓名" label="姓名" width="100" />
        <el-table-column prop="岗位" label="岗位" min-width="120" />
        <el-table-column label="原班次日期" width="150">
          <template #default="{ row }">{{ row.original_date }} {{ row.original_time || '' }}</template>
        </el-table-column>
        <el-table-column label="调休后日期" width="150">
          <template #default="{ row }">{{ row.new_date }} {{ row.new_time || '' }}</template>
        </el-table-column>
        <el-table-column prop="reason" label="调休原因" min-width="150" show-overflow-tooltip />
        <el-table-column prop="approver" label="审批人" width="100" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag v-if="row.status==='approved'" type="success" size="small">已通过</el-tag>
            <el-tag v-else-if="row.status==='rejected'" type="danger" size="small">已驳回</el-tag>
            <el-tag v-else type="warning" size="small">待审批</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button size="small" type="success" @click="approve(row.id)">通过</el-button>
              <el-button size="small" type="danger" @click="reject(row.id)">驳回</el-button>
            </template>
            <span v-else style="color:#999">-</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增调休弹窗 -->
    <el-dialog v-model="dialogVisible" title="新增调休" width="500px" destroy-on-close>
      <div style="background:#f5f7fa;border-radius:8px;padding:16px;margin-bottom:16px">
        <el-row :gutter="12">
          <el-col :span="16">
            <el-input v-model="lookupKey" placeholder="输入工号或姓名，从花名册自动带入信息" clearable @keyup.enter="doLookup" />
          </el-col>
          <el-col :span="8">
            <el-button type="primary" style="background-color:#ec6921;border-color:#ec6921" :loading="lookingUp" @click="doLookup">查找带入</el-button>
          </el-col>
        </el-row>
        <div v-if="lookupHint" style="margin-top:6px;font-size:12px;color:#999">{{ lookupHint }}</div>
      </div>
      <el-form :model="form" label-width="110px">
        <el-form-item label="选择员工" required>
          <el-select v-model="form.employee_no" placeholder="选择员工" style="width:100%" :disabled="!!lookupKey">
            <el-option v-for="e in employees" :key="e.工号" :label="e.姓名 + '（' + e.工号 + '）'" :value="e.工号" />
          </el-select>
        </el-form-item>
        <el-form-item label="原班次日期" required>
          <el-date-picker v-model="form.original_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="原班次时间">
          <el-time-select v-model="form.original_time" start="08:00" step="00:30" end="22:00" placeholder="选择时间" style="width:100%" />
        </el-form-item>
        <el-form-item label="调休后日期" required>
          <el-date-picker v-model="form.new_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="调休后时间">
          <el-time-select v-model="form.new_time" start="08:00" step="00:30" end="22:00" placeholder="选择时间" style="width:100%" />
        </el-form-item>
        <el-form-item label="调休原因">
          <el-input v-model="form.reason" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { get, post, put } from '@/api/request'
import { lookupRoster } from '@/api/roster'

const adjustments = ref([])
const employees = ref([])
const dialogVisible = ref(false)
const form = ref({ employee_no: '', original_date: '', original_time: '', new_date: '', new_time: '', reason: '' })
const lookupKey = ref('')
const lookingUp = ref(false)
const lookupHint = ref('')
const loadAdjustments = async () => {
  const res = await get('/work-hours/adjustments')
  adjustments.value = res.items || []
}

const loadEmployees = async () => {
  try {
    const res = await get('/roster/?status=all&limit=1000')
    employees.value = res.items || []
    console.log('[loadEmployees] loaded:', employees.value.length)
  } catch (e) {
    console.error('[loadEmployees] failed:', e)
    employees.value = []
  }
}

const openDialog = async () => {
  lookupKey.value = ''; lookupHint.value = ''
  form.value = { employee_no: '', original_date: '', original_time: '', new_date: '', new_time: '', reason: '' }
  dialogVisible.value = true
  if (employees.value.length === 0) await loadEmployees()
}

const doLookup = async () => {
  if (!lookupKey.value.trim()) { lookupHint.value = '请输入工号或姓名'; return }
  lookingUp.value = true; lookupHint.value = ''
  try {
    console.log('[lookup] employees count:', employees.value.length)
    if (employees.value.length === 0) {
      console.log('[lookup] loading employees...')
      await loadEmployees()
      console.log('[lookup] employees loaded:', employees.value.length)
    }
    const res = await lookupRoster(lookupKey.value.trim())
    console.log('[lookup] roster result:', res)
    if (!res) { lookupHint.value = '花名册中未找到此人'; return }
    lookupHint.value = `✓ 已找到：${res.姓名}（${res.工号}）-${res.部门}-${res.岗位 || '无岗位'}`
    form.value.employee_no = res.工号 || ''
    lookupKey.value = ''  // 清空后select可显示并可编辑
  } catch (e) {
    console.error('[lookup] error:', e)
    lookupHint.value = '查找失败，请重试'
  } finally { lookingUp.value = false }
}

const save = async () => {
  if (!form.value.employee_no) { ElMessage.warning('请选择员工'); return }
  if (!form.value.original_date) { ElMessage.warning('请填写原班次日期'); return }
  if (!form.value.new_date) { ElMessage.warning('请填写调休后日期'); return }
  await post('/work-hours/adjustments', form.value)
  ElMessage.success('调休记录已提交')
  dialogVisible.value = false
  loadAdjustments()
}

const approve = async (id) => {
  await put(`/work-hours/adjustments/${id}/approve`)
  ElMessage.success('已通过')
  loadAdjustments()
}

const reject = async (id) => {
  await put(`/work-hours/adjustments/${id}/reject`)
  ElMessage.success('已驳回')
  loadAdjustments()
}

onMounted(() => { loadAdjustments(); loadEmployees() })
</script>

<style scoped>
.adjustments-page { padding: 24px; }
.page-header { margin-bottom: 20px; }
.page-header h2 { margin: 0 0 4px; font-size: 18px; color: #333; }
.subtitle { margin: 0; font-size: 13px; color: #999; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
