<template>
  <div class="work-hours-page">
    <div class="page-header">
      <h2>工时配置</h2>
      <p class="subtitle">配置各部门的休息时间，系统将据此自动计算员工实际工时</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>部门休息时间配置</span>
          <el-tag type="info">共 {{ breaks.length }} 个部门</el-tag>
        </div>
      </template>

      <el-table :data="breaks" stripe style="width: 100%">
        <el-table-column prop="department_name" label="部门" min-width="160" />
        <el-table-column label="休息开始" width="140">
          <template #default="{ row }">
            <el-time-picker
              v-model="row._break_start"
              format="HH:mm"
              value-format="HH:mm"
              size="small"
              style="width: 110px"
              :disabled="row._saving"
              @change="saveBreak(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="休息结束" width="140">
          <template #default="{ row }">
            <el-time-picker
              v-model="row._break_end"
              format="HH:mm"
              value-format="HH:mm"
              size="small"
              style="width: 110px"
              :disabled="row._saving"
              @change="saveBreak(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="休息时长" width="120">
          <template #default="{ row }">
            <span class="minutes-tag">{{ row.break_minutes }} 分钟</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '已启用' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button
              v-if="row._saving"
              type="primary"
              size="small"
              loading
            >
              保存中
            </el-button>
            <el-tag v-else-if="row._saved" type="success" size="small">
              已保存
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 说明 -->
    <el-card style="margin-top: 16px;">
      <template #header>
        <span>计算说明</span>
      </template>
      <el-form label-width="120px">
        <el-form-item label="工时公式">
          <el-tag>实际工时 = 下班打卡时间 - 上班打卡时间 - 休息时长</el-tag>
        </el-form-item>
        <el-form-item label="示例">
          <div style="color: #666; font-size: 13px;">
            某员工上班打卡 08:00，下班打卡 17:30，部门休息时间 12:00-13:00（60分钟）<br/>
            则：17:30 - 08:00 - 60分钟 = 8.5 小时
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDepartmentBreaks, saveDepartmentBreak } from '@/api/workHours'
import { ElMessage } from 'element-plus'

const breaks = ref([])

onMounted(async () => {
  await loadBreaks()
})

async function loadBreaks() {
  try {
    const data = await getDepartmentBreaks()
    // 附加编辑状态
    breaks.value = data.map(item => ({
      ...item,
      _break_start: item.break_start,
      _break_end: item.break_end,
      _saving: false,
      _saved: false,
    }))
  } catch (e) {
    ElMessage.error('加载失败')
  }
}

async function saveBreak(row) {
  // 计算休息时长（分钟）
  const [startH, startM] = row._break_start.split(':').map(Number)
  const [endH, endM] = row._break_end.split(':').map(Number)
  const minutes = (endH * 60 + endM) - (startH * 60 + startM)

  if (minutes <= 0) {
    ElMessage.warning('休息结束时间必须晚于开始时间')
    row._break_start = row.break_start
    row._break_end = row.break_end
    return
  }

  row._saving = true
  row._saved = false
  try {
    await saveDepartmentBreak({
      department_id: row.department_id,
      break_start: row._break_start,
      break_end: row._break_end,
      break_minutes: minutes,
    })
    row.break_start = row._break_start
    row.break_end = row._break_end
    row.break_minutes = minutes
    row._saved = true
    setTimeout(() => { row._saved = false }, 2000)
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error('保存失败')
    row._break_start = row.break_start
    row._break_end = row.break_end
  } finally {
    row._saving = false
  }
}
</script>

<style scoped>
.work-hours-page {
  padding: 20px;
}
.page-header h2 {
  margin: 0 0 4px 0;
}
.subtitle {
  margin: 0;
  color: #999;
  font-size: 13px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.minutes-tag {
  font-weight: bold;
  color: #ec6921;
}
</style>
