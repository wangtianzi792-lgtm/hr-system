<template>
  <div class="shifts-page">
    <div class="page-header">
      <h2>班次配置</h2>
      <p class="subtitle">定义上班时间、午休时长、夜班标记，系统据此计算加班工时</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>班次列表</span>
          <el-button type="primary" @click="openDialog()">
            <el-icon><Plus /></el-icon> 新增班次
          </el-button>
        </div>
      </template>

      <el-table :data="shifts" stripe>
        <el-table-column prop="name" label="班次名称" min-width="120" />
        <el-table-column label="上班时间" width="100">
          <template #default="{ row }">{{ row.start_time }}</template>
        </el-table-column>
        <el-table-column label="下班时间" width="100">
          <template #default="{ row }">{{ row.end_time }}</template>
        </el-table-column>
        <el-table-column label="午休(分钟)" width="100" prop="break_duration" />
        <el-table-column label="夜班" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.is_night_shift" type="warning" size="small">是</el-tag>
            <span v-else style="color:#999">否</span>
          </template>
        </el-table-column>
        <el-table-column label="加班阈值(分钟)" width="130">
          <template #default="{ row }">
            {{ row.overtime_threshold > 0 ? `超过${row.overtime_threshold}分钟算加班` : '无' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="删除该班次？" @confirm="deleteShift(row.id)">
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editing.id ? '编辑班次' : '新增班次'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="班次名称" required>
          <el-input v-model="form.name" placeholder="如：常日班、夜班、倒班" />
        </el-form-item>
        <el-form-item label="上班时间" required>
          <el-time-picker v-model="form.start_time" format="HH:mm" value-format="HH:mm" style="width:100%" />
        </el-form-item>
        <el-form-item label="下班时间" required>
          <el-time-picker v-model="form.end_time" format="HH:mm" value-format="HH:mm" style="width:100%" />
        </el-form-item>
        <el-form-item label="午休时长(分钟)">
          <el-input-number v-model="form.break_duration" :min="0" :max="180" />
        </el-form-item>
        <el-form-item label="加班阈值(分钟)">
          <el-input-number v-model="form.overtime_threshold" :min="0" :max="480" :step="30" />
          <div style="color:#999;font-size:12px;margin-top:4px">超过该分钟数才计入加班，默认0表示不限制</div>
        </el-form-item>
        <el-form-item label="夜班">
          <el-switch v-model="form.is_night_shift" />
          <div style="color:#999;font-size:12px;margin-top:4px">夜班跨越零点，下班时间为次日</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveShift">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { get, post, put, del } from '@/api/request'

const shifts = ref([])
const dialogVisible = ref(false)
const editing = ref({})
const form = ref({
  name: '',
  start_time: '08:30',
  end_time: '17:30',
  break_duration: 60,
  is_night_shift: false,
  overtime_threshold: 0
})

const loadShifts = async () => {
  const res = await get('/api/work-hours/shifts')
  shifts.value = res.items || []
}

const openDialog = (row = null) => {
  if (row) {
    editing.value = row
    form.value = { ...row }
  } else {
    editing.value = {}
    form.value = { name: '', start_time: '08:30', end_time: '17:30', break_duration: 60, is_night_shift: false, overtime_threshold: 0 }
  }
  dialogVisible.value = true
}

const saveShift = async () => {
  if (!form.value.name) { ElMessage.warning('请填写班次名称'); return }
  if (editing.value.id) {
    await put(`/api/work-hours/shifts/${editing.value.id}`, form.value)
    ElMessage.success('更新成功')
  } else {
    await post('/api/work-hours/shifts', form.value)
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  loadShifts()
}

const deleteShift = async (id) => {
  await del(`/api/work-hours/shifts/${id}`)
  ElMessage.success('删除成功')
  loadShifts()
}

onMounted(loadShifts)
</script>

<style scoped>
.shifts-page { padding: 24px; }
.page-header { margin-bottom: 20px; }
.page-header h2 { margin: 0 0 4px; font-size: 18px; color: #333; }
.subtitle { margin: 0; font-size: 13px; color: #999; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
