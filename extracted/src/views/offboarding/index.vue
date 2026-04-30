<template>
  <div class="offboarding-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>离职管理</span>
          <el-button type="primary" style="background-color:#ec6921;border-color:#ec6921" @click="showAddDialog">
            新增离职
          </el-button>
        </div>
      </template>

      <el-row :gutter="20" style="margin-bottom:16px">
        <el-col :span="6">
          <el-input v-model="searchQuery" placeholder="搜索工号/姓名" clearable @keyup.enter="loadData" />
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterDept" placeholder="按部门筛选" clearable style="width:100%">
            <el-option v-for="d in deptOptions" :key="d" :label="d" :value="d" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterStatus" placeholder="按状态筛选" clearable style="width:100%">
            <el-option label="待审批" value="pending" />
            <el-option label="部门已通过" value="dept_approved" />
            <el-option label="总经理已通过" value="gm_approved" />
            <el-option label="已离职" value="confirmed" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已撤回" value="withdrawn" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" style="background-color:#ec6921;border-color:#ec6921" @click="loadData">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>

      <el-table :data="filteredList" v-loading="loading" stripe style="width:100%">
        <el-table-column prop="工号" label="工号" width="110" />
        <el-table-column prop="姓名" label="姓名" width="90" />
        <el-table-column prop="部门" label="部门" min-width="110" />
        <el-table-column prop="岗位" label="岗位" min-width="120">
          <template #default="{ row }">
            {{ row.岗位 }}
            <el-tag v-if="isManagerLevel(row.岗位)" type="warning" size="small" style="margin-left:4px">经理级</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="离职日期" label="计划离职日期" width="115" />
        <el-table-column label="审批状态" width="120">
          <template #default="{ row }">
            <el-tag :type="approvalTagType(row.审批状态)">{{ approvalText(row.审批状态) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="部门审批" width="130">
          <template #default="{ row }">
            <span v-if="row.部门审批人" style="font-size:12px">{{ row.部门审批人 }}<br/><span style="color:#999">{{ row.部门审批时间 }}</span></span>
            <el-tag v-else type="info" size="small">待审批</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="总经理审批" width="130">
          <template #default="{ row }">
            <span v-if="row.总经理审批人" style="font-size:12px">{{ row.总经理审批人 }}<br/><span style="color:#999">{{ row.总经理审批时间 }}</span></span>
            <span v-else-if="!isManagerLevel(row.岗位)" style="color:#ccc;font-size:12px">不需此级</span>
            <el-tag v-else type="info" size="small">待审批</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="人事审批" width="130">
          <template #default="{ row }">
            <span v-if="row.人事审批人" style="font-size:12px">{{ row.人事审批人 }}<br/><span style="color:#999">{{ row.人事审批时间 }}</span></span>
            <span v-else-if="row.审批状态 === 'rejected'" style="color:#999">—</span>
            <el-tag v-else type="info" size="small">待审批</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="离职原因" label="离职原因" min-width="120" show-overflow-tooltip />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <template v-if="row.审批状态 === 'pending'">
              <el-button type="primary" link size="small" @click="openDeptApprove(row)">部门审批</el-button>
            </template>
            <template v-if="row.审批状态 === 'dept_approved' && isManagerLevel(row.岗位)">
              <el-button type="success" link size="small" @click="openGmApprove(row)">总经理审批</el-button>
            </template>
            <template v-if="row.审批状态 === 'dept_approved' && !isManagerLevel(row.岗位) || row.审批状态 === 'gm_approved'">
              <el-button type="success" link size="small" @click="openHrApprove(row)">人事审批</el-button>
            </template>
            <el-button type="warning" link size="small" @click="withdrawRow(row)" v-if="row.审批状态 !== 'withdrawn'">撤回</el-button>
            <el-button type="primary" link size="small" @click="editRow(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteRow(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top:16px;display:flex;justify-content:flex-end">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[30,50,100]"
          :total="total"
          layout="total,sizes,prev,pager,next"
          @current-change="loadData"
          @size-change="loadData"
        />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑离职信息' : '新增离职'" width="650px" destroy-on-close>
      <div v-if="!isEdit" style="background:#f5f7fa;border-radius:8px;padding:16px;margin-bottom:16px">
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
      <el-form :model="form" label-width="120px">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="工号"><el-input v-model="form.工号" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="姓名"><el-input v-model="form.姓名" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="性别"><el-select v-model="form.性别" style="width:100%">
              <el-option label="男" value="男" /><el-option label="女" value="女" />
            </el-select></el-form-item>
          </el-col>
          <el-col :span="12"><el-form-item label="联系电话"><el-input v-model="form.联系电话" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="部门"><el-select v-model="form.部门" style="width:100%">
              <el-option v-for="d in deptOptions" :key="d" :label="d" :value="d" />
            </el-select></el-form-item>
          </el-col>
          <el-col :span="12"><el-form-item label="岗位"><el-input v-model="form.岗位" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="离职日期"><el-date-picker v-model="form.离职日期" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="离职原因"><el-input v-model="form.离职原因" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.备注" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" style="background-color:#ec6921;border-color:#ec6921" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 部门审批弹窗 -->
    <el-dialog v-model="deptApproveVisible" title="部门审批" width="500px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="离职员工">{{ currentRow?.姓名 }} ({{ currentRow?.工号 }})</el-form-item>
        <el-form-item label="岗位">{{ currentRow?.岗位 }}</el-form-item>
        <el-form-item label="离职原因">{{ currentRow?.离职原因 }}</el-form-item>
        <el-form-item label="审批意见"><el-input v-model="deptApproveForm.comment" type="textarea" :rows="3" placeholder="请输入审批意见（选填）" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deptApproveVisible=false">取消</el-button>
        <el-button type="danger" @click="submitDeptApprove(false)">拒绝</el-button>
        <el-button type="success" style="background-color:#67c23a;border-color:#67c23a" @click="submitDeptApprove(true)">通过</el-button>
      </template>
    </el-dialog>

    <!-- 总经理审批弹窗 -->
    <el-dialog v-model="gmApproveVisible" title="总经理审批" width="500px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="离职员工">{{ currentRow?.姓名 }} ({{ currentRow?.工号 }})</el-form-item>
        <el-form-item label="岗位"><span style="color:#e6a23c">{{ currentRow?.岗位 }}</span>（经理级）</el-form-item>
        <el-form-item label="部门审批"><span style="color:#67c23a">✓ 已通过</span><span style="margin-left:8px;color:#999">{{ currentRow?.部门审批人 }}</span></el-form-item>
        <el-form-item label="审批意见"><el-input v-model="gmApproveForm.comment" type="textarea" :rows="3" placeholder="请输入审批意见（选填）" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="gmApproveVisible=false">取消</el-button>
        <el-button type="danger" @click="submitGmApprove(false)">拒绝</el-button>
        <el-button type="success" style="background-color:#67c23a;border-color:#67c23a" @click="submitGmApprove(true)">通过</el-button>
      </template>
    </el-dialog>

    <!-- 人事审批弹窗 -->
    <el-dialog v-model="hrApproveVisible" title="人事审批" width="500px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="离职员工">{{ currentRow?.姓名 }} ({{ currentRow?.工号 }})</el-form-item>
        <el-form-item label="岗位">{{ currentRow?.岗位 }} <el-tag v-if="isManagerLevel(currentRow?.岗位)" type="warning" size="small" style="margin-left:8px">经理级</el-tag></el-form-item>
        <el-form-item v-if="isManagerLevel(currentRow?.岗位)" label="总经理审批"><span style="color:#67c23a">✓ 已通过</span><span style="margin-left:8px;color:#999">{{ currentRow?.总经理审批人 }}</span></el-form-item>
        <el-form-item v-else label="部门审批"><span style="color:#67c23a">✓ 已通过</span><span style="margin-left:8px;color:#999">{{ currentRow?.部门审批人 }}</span></el-form-item>
        <el-form-item label="审批意见"><el-input v-model="hrApproveForm.comment" type="textarea" :rows="3" placeholder="请输入审批意见（选填）" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="hrApproveVisible=false">取消</el-button>
        <el-button type="danger" @click="submitHrApprove(false)">拒绝</el-button>
        <el-button type="success" style="background-color:#67c23a;border-color:#67c23a" @click="submitHrApprove(true)">确认离职</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRosterDepartments, lookupRoster } from '@/api/roster'
import { getOffboardingList, createOffboarding, updateOffboarding, deleteOffboarding, approveDept, approveGm, approveHr, withdrawOffboarding } from '@/api/offboarding'

const searchQuery = ref('')
const filterDept = ref('')
const filterStatus = ref('')
const deptOptions = ref([])
const page = ref(1)
const pageSize = ref(30)
const total = ref(0)
const loading = ref(false)
const allData = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const deptApproveVisible = ref(false)
const gmApproveVisible = ref(false)
const hrApproveVisible = ref(false)
const currentRow = ref(null)
const lookupKey = ref('')
const lookingUp = ref(false)
const lookupHint = ref('')

const deptApproveForm = ref({ comment: '' })
const gmApproveForm = ref({ comment: '' })
const hrApproveForm = ref({ comment: '' })

const form = ref({
  工号: '', 姓名: '', 性别: '男', 联系电话: '', 部门: '', 岗位: '', 离职日期: '', 状态: 'pending', 离职原因: '', 备注: ''
})

const isManagerLevel = (pos) => {
  if (!pos) return false
  const kw = ['经理', '总监', '总经理', '副总经理', '董事长', '总裁', 'VP']
  return kw.some(k => pos.toUpperCase().includes(k.toUpperCase()))
}

const filteredList = computed(() => {
  let list = allData.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(r => (r.工号 && r.工号.toLowerCase().includes(q)) || (r.姓名 && r.姓名.toLowerCase().includes(q)))
  }
  if (filterDept.value) list = list.filter(r => r.部门 === filterDept.value)
  if (filterStatus.value) list = list.filter(r => (r.审批状态 || r.状态) === filterStatus.value)
  return list
})

const approvalText = (s) => ({ pending: '待审批', dept_approved: '部门已通过', gm_approved: '总经理已通过', confirmed: '已离职', rejected: '已拒绝', withdrawn: '已撤回' }[s] || s)
const approvalTagType = (s) => ({ pending: 'warning', dept_approved: 'primary', gm_approved: 'warning', confirmed: 'success', rejected: 'info', withdrawn: 'info' }[s] || '')

const loadData = async () => {
  loading.value = true
  try {
    const res = await getOffboardingList({
      skip: (page.value - 1) * pageSize.value, limit: pageSize.value,
      search: searchQuery.value || undefined, department: filterDept.value || undefined, status: filterStatus.value || undefined,
    })
    allData.value = res.items || []
    total.value = res.total || 0
  } catch (e) { ElMessage.error('加载失败') } finally { loading.value = false }
}

const resetFilters = () => { searchQuery.value = ''; filterDept.value = ''; filterStatus.value = ''; page.value = 1; loadData() }

const doLookup = async () => {
  if (!lookupKey.value.trim()) { lookupHint.value = '请输入工号或姓名'; return }
  lookingUp.value = true; lookupHint.value = ''
  try {
    const res = await lookupRoster(lookupKey.value.trim())
    if (!res) { lookupHint.value = '花名册中未找到此人'; return }
    lookupHint.value = `✓ 已找到：${res.姓名}（${res.工号}）-${res.部门}-${res.岗位 || '无岗位'}`
    form.value.工号 = res.工号 || ''
    form.value.姓名 = res.姓名 || ''
    form.value.性别 = res.性别 || '男'
    form.value.联系电话 = res.联系电话 || ''
    form.value.部门 = res.部门 || ''
    form.value.岗位 = res.岗位 || ''
  } catch (e) { lookupHint.value = '查找失败，请重试' } finally { lookingUp.value = false }
}

const showAddDialog = () => {
  isEdit.value = false; lookupKey.value = ''; lookupHint.value = ''
  Object.keys(form.value).forEach(k => {
    if (k === '性别') form.value[k] = '男'
    else if (k === '状态') form.value[k] = 'pending'
    else form.value[k] = ''
  })
  dialogVisible.value = true
}

const editRow = (row) => {
  isEdit.value = true; lookupKey.value = ''; lookupHint.value = ''
  Object.keys(form.value).forEach(k => form.value[k] = row[k] || '')
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!form.value.工号 && !form.value.姓名) { ElMessage.warning('请填写工号或姓名'); return }
  try {
    if (isEdit.value) { await updateOffboarding(form.value); ElMessage.success('更新成功') }
    else { await createOffboarding(form.value); ElMessage.success('新增成功') }
    dialogVisible.value = false; loadData()
  } catch (e) { ElMessage.error('操作失败') }
}

const deleteRow = async (row) => {
  const isConfirmed = row.审批状态 === 'confirmed'
  const msg = isConfirmed ? `确定删除 "${row.姓名}" 的离职记录吗？该员工已不在花名册中。` : `确定删除 "${row.姓名}" 的离职记录吗？`
  try {
    await ElMessageBox.confirm(msg, '确认删除', { type: 'warning' })
    await deleteOffboarding(row.id)
    ElMessage.success('删除成功'); loadData()
  } catch (e) { if (e !== 'cancel') ElMessage.error('删除失败') }
}

const openDeptApprove = (row) => { currentRow.value = row; deptApproveForm.value.comment = ''; deptApproveVisible.value = true }
const openGmApprove = (row) => { currentRow.value = row; gmApproveForm.value.comment = ''; gmApproveVisible.value = true }
const openHrApprove = (row) => { currentRow.value = row; hrApproveForm.value.comment = ''; hrApproveVisible.value = true }

const submitDeptApprove = async (approved) => {
  try {
    await approveDept(currentRow.value.id, { approved, comment: deptApproveForm.value.comment, approver: '部门审批人' })
    ElMessage.success(approved ? '已通过部门审批' : '已拒绝')
    deptApproveVisible.value = false; loadData()
  } catch (e) { ElMessage.error('审批操作失败') }
}

const submitGmApprove = async (approved) => {
  try {
    await approveGm(currentRow.value.id, { approved, comment: gmApproveForm.value.comment, approver: '总经理' })
    ElMessage.success(approved ? '已通过总经理审批' : '已拒绝')
    gmApproveVisible.value = false; loadData()
  } catch (e) { ElMessage.error('审批操作失败') }
}

const submitHrApprove = async (approved) => {
  try {
    await approveHr(currentRow.value.id, { approved, comment: hrApproveForm.value.comment, approver: '人事审批人' })
    ElMessage.success(approved ? '已确认离职' : '已拒绝')
    hrApproveVisible.value = false; loadData()
  } catch (e) { ElMessage.error('审批操作失败') }
}

const withdrawRow = async (row) => {
  try {
    await ElMessageBox.confirm(`确定撤回 "${row.姓名}" 的离职申请吗？员工将恢复入职。`, '确认撤回', { type: 'warning' })
    await withdrawOffboarding(row.id, {})
    ElMessage.success('已撤回，员工恢复入职')
    loadData()
  } catch (e) { if (e !== 'cancel') ElMessage.error('撤回失败') }
}

onMounted(() => { loadData(); getRosterDepartments().then(res => { deptOptions.value = res || [] }).catch(() => {}) })
</script>

<style scoped>
.offboarding-container { padding: 0; }
.card-header { display:flex; justify-content:space-between; align-items:center; }
</style>
