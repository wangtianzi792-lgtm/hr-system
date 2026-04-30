<template>
  <div class="shifts-page">
    <el-card class="search-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="8">
          <el-input v-model="searchKey" placeholder="搜索班次名称" clearable @keyup.enter="fetchShifts">
            <template #append>
              <el-button @click="fetchShifts"><el-icon><Search /></el-icon></el-button>
            </template>
          </el-input>
        </el-col>
        <el-col :span="16" style="text-align: right;">
          <el-button type="primary" @click="showAddDialog" style="background:#ec6921;border-color:#ec6921;">
            <el-icon><Plus /></el-icon>新增班次
          </el-button>
          <el-button @click="fetchShifts"><el-icon><Refresh /></el-icon>刷新</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card style="margin-top:16px;">
      <el-table :data="shiftList" v-loading="loading" style="width:100%">
        <el-table-column prop="name" label="班次名称" min-width="120" />
        <el-table-column prop="shift_type" label="类型" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.shift_type === 'day' ? 'success' : scope.row.shift_type === 'night' ? 'warning' : 'info'">
              {{ shiftTypeMap[scope.row.shift_type] || scope.row.shift_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="上班打卡时段" width="180">
          <template #default="scope">
            {{ scope.row.check_in_start }} ~ {{ scope.row.check_in_end }}
          </template>
        </el-table-column>
        <el-table-column label="下班打卡时段" width="180">
          <template #default="scope">
            {{ scope.row.check_out_start }} ~ {{ scope.row.check_out_end }}
          </template>
        </el-table-column>
        <el-table-column prop="work_hours" label="工时" width="80" align="center" />
        <el-table-column prop="color" label="颜色标记" width="80" align="center">
          <template #default="scope">
            <span v-if="scope.row.color" :style="{ color: scope.row.color, fontWeight: 'bold' }">●</span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="editShift(scope.row)" style="color:#ec6921;">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="currentPage" v-model:page-size="pageSize"
        :total="total" :page-sizes="[10,20,50]"
        layout="total,sizes,prev,pager,next"
        style="margin-top:16px;justify-content:flex-end;"
        @size-change="fetchShifts" @current-change="fetchShifts"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑班次' : '新增班次'" width="560px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="130px">
        <el-form-item label="班次名称" prop="name">
          <el-input v-model="form.name" placeholder="例如：早班" />
        </el-form-item>
        <el-form-item label="班次类型" prop="shift_type">
          <el-select v-model="form.shift_type" style="width:100%">
            <el-option label="白班" value="day" />
            <el-option label="夜班" value="night" />
            <el-option label="弹性班" value="flex" />
            <el-option label="自由班" value="free" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="上班开始" prop="check_in_start">
              <el-time-picker v-model="form.check_in_start" format="HH:mm" value-format="HH:mm" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="上班结束" prop="check_in_end">
              <el-time-picker v-model="form.check_in_end" format="HH:mm" value-format="HH:mm" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="下班开始" prop="check_out_start">
              <el-time-picker v-model="form.check_out_start" format="HH:mm" value-format="HH:mm" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="下班结束" prop="check_out_end">
              <el-time-picker v-model="form.check_out_end" format="HH:mm" value-format="HH:mm" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="工时" prop="work_hours">
              <el-input-number v-model="form.work_hours" :min="0" :max="24" :step="0.5" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="颜色标记">
              <el-color-picker v-model="form.color" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="可选备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitLoading" style="background:#ec6921;border-color:#ec6921;">
          {{ isEdit ? '保存' : '新增' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getShifts, createShift, updateShift, deleteShift } from '@/api/shifts'

const shiftList = ref([])
const loading = ref(false)
const searchKey = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)

const shiftTypeMap = {
  day: '白班',
  night: '夜班',
  flex: '弹性班',
  free: '自由班'
}

const defaultForm = () => ({
  name: '', shift_type: 'day',
  check_in_start: '08:00', check_in_end: '09:00',
  check_out_start: '17:30', check_out_end: '18:30',
  work_hours: 8.0, color: '', remark: ''
})
const form = reactive(defaultForm())

const rules = {
  name: [{ required: true, message: '请输入班次名称', trigger: 'blur' }],
  shift_type: [{ required: true, message: '请选择班次类型', trigger: 'change' }],
  check_in_start: [{ required: true, message: '请选择时间', trigger: 'change' }],
  check_in_end: [{ required: true, message: '请选择时间', trigger: 'change' }],
  check_out_start: [{ required: true, message: '请选择时间', trigger: 'change' }],
  check_out_end: [{ required: true, message: '请选择时间', trigger: 'change' }],
  work_hours: [{ required: true, message: '请输入工时', trigger: 'blur' }]
}

const fetchShifts = async () => {
  loading.value = true
  try {
    const res = await getShifts({ skip: (currentPage.value - 1) * pageSize.value, limit: pageSize.value })
    const data = Array.isArray(res) ? res : (res.items || [])
    shiftList.value = data
    total.value = Array.isArray(res) ? res.length : (res.total || data.length)
  } catch (e) {
    ElMessage.error('加载班次失败')
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  isEdit.value = false
  Object.assign(form, defaultForm())
  dialogVisible.value = true
}

const editShift = (row) => {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    name: row.name, shift_type: row.shift_type,
    check_in_start: row.check_in_start, check_in_end: row.check_in_end,
    check_out_start: row.check_out_start, check_out_end: row.check_out_end,
    work_hours: row.work_hours, color: row.color || '', remark: row.remark || ''
  })
  dialogVisible.value = true
}

const submitForm = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    if (isEdit.value) {
      await updateShift(form.id, form)
      ElMessage.success('班次已更新')
    } else {
      await createShift(form)
      ElMessage.success('班次已创建')
    }
    dialogVisible.value = false
    fetchShifts()
  } catch (e) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定删除班次 "' + row.name + '"？', '确认删除', { type: 'warning' })
    .then(async () => {
      try {
        await deleteShift(row.id)
        ElMessage.success('删除成功')
        fetchShifts()
      } catch (e) {
        ElMessage.error('删除失败')
      }
    }).catch(() => {})
}

onMounted(fetchShifts)
</script>

<style scoped>
.shifts-page { padding: 0; }
.search-card { margin-bottom: 0; }
</style>
