<template>
  <div class="devices-page">
    <el-card class="search-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="12">
          <el-input v-model="searchKey" placeholder="搜索设备名称/IP地址" clearable @keyup.enter="fetchDevices">
            <template #append>
              <el-button @click="fetchDevices"><el-icon><Search /></el-icon></el-button>
            </template>
          </el-input>
        </el-col>
        <el-col :span="12" style="text-align: right;">
          <el-button type="primary" @click="showAddDialog" style="background:#ec6921;border-color:#ec6921;">
            <el-icon><Plus /></el-icon>添加设备
          </el-button>
          <el-button @click="fetchDevices"><el-icon><Refresh /></el-icon>刷新</el-button>
          <el-button type="warning" @click="checkAllStatus" :loading="checkingAll">
            <el-icon><Connection /></el-icon>检测全部
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="16" style="margin-top:16px;">
      <el-col :span="8" v-for="device in deviceList" :key="device.id">
        <el-card class="device-card" :class="{ offline: device.status !== 'online' }">
          <div class="device-header">
            <div class="device-icon">
              <el-icon :size="32"><Monitor /></el-icon>
            </div>
            <div class="device-info">
              <div class="device-name">{{ device.name }}</div>
              <div class="device-type">{{ device.device_type }} | {{ device.location }}</div>
            </div>
            <el-tag :type="device.status === 'online' ? 'success' : 'danger'" size="small">
              {{ device.status === 'online' ? '在线' : '离线' }}
            </el-tag>
          </div>
          <div class="device-body">
            <div class="device-detail">
              <span class="label">IP地址:</span>
              <span class="value">{{ device.ip_address }}:{{ device.port }}</span>
            </div>
            <div class="device-detail">
              <span class="label">序列号:</span>
              <span class="value">{{ device.serial_number || '-' }}</span>
            </div>
            <div class="device-detail">
              <span class="label">最后同步:</span>
              <span class="value">{{ device.last_sync || '未同步' }}</span>
            </div>
          </div>
          <div class="device-actions">
            <el-button size="small" @click="checkStatus(device)" :loading="device.checking">
              <el-icon><Connection /></el-icon>检测
            </el-button>
            <el-button size="small" type="primary" @click="syncDeviceData(device)" :loading="device.syncing" style="background:#ec6921;border-color:#ec6921;">
              <el-icon><Refresh /></el-icon>同步
            </el-button>
            <el-button size="small" type="success" @click="downloadDeviceRecords(device)" :loading="device.downloading">
              <el-icon><Download /></el-icon>下载打卡
            </el-button>
            <el-button size="small" @click="editDevice(device)" style="color:#ec6921;">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(device)">
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加/编辑设备对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑设备' : '添加设备'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="设备名称" prop="name">
          <el-input v-model="form.name" placeholder="例如：xFace100-主机" />
        </el-form-item>
        <el-form-item label="设备类型" prop="device_type">
          <el-select v-model="form.device_type" style="width:100%">
            <el-option label="xFace100" value="xFace100" />
            <el-option label="xFace200" value="xFace200" />
            <el-option label="iFace系列" value="iFace" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="16">
            <el-form-item label="IP地址" prop="ip_address">
              <el-input v-model="form.ip_address" placeholder="192.168.1.201" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="端口" prop="port">
              <el-input-number v-model="form.port" :min="1" :max="65535" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="安装位置" prop="location">
          <el-input v-model="form.location" placeholder="例如：一楼大门" />
        </el-form-item>
        <el-form-item label="序列号">
          <el-input v-model="form.serial_number" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitLoading" style="background:#ec6921;border-color:#ec6921;">
          {{ isEdit ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDevices, createDevice, updateDevice, deleteDevice, checkDeviceStatus, syncDevice, downloadRecords } from '@/api/devices'

const deviceList = ref([])
const loading = ref(false)
const checkingAll = ref(false)
const searchKey = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  name: '',
  device_type: 'xFace100',
  ip_address: '',
  port: 4370,
  location: '',
  serial_number: ''
})

const rules = {
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  device_type: [{ required: true, message: '请选择设备类型', trigger: 'change' }],
  ip_address: [{ required: true, message: '请输入IP地址', trigger: 'blur' }],
  port: [{ required: true, message: '请输入端口', trigger: 'blur' }],
  location: [{ required: true, message: '请输入安装位置', trigger: 'blur' }]
}

const fetchDevices = async (checkStatus = false) => {
  loading.value = true
  try {
    const res = await getDevices({ limit: 100 }, checkStatus)
    const data = Array.isArray(res) ? res : (res.items || [])
    // 保留现有的 checking/syncing/downloading 状态
    const statusMap = {}
    deviceList.value.forEach(d => {
      statusMap[d.id] = { checking: d.checking, syncing: d.syncing, downloading: d.downloading }
    })
    deviceList.value = data.map(d => ({
      ...d,
      checking: statusMap[d.id]?.checking || false,
      syncing: statusMap[d.id]?.syncing || false,
      downloading: statusMap[d.id]?.downloading || false
    }))
  } catch (e) {
    console.error('加载设备失败', e)
    ElMessage.error('加载设备失败')
  } finally {
    loading.value = false
  }
}

const checkAllStatus = async () => {
  checkingAll.value = true
  try {
    await fetchDevices(true)
    ElMessage.success('设备状态检测完成')
  } catch (e) {
    ElMessage.error('检测失败')
  } finally {
    checkingAll.value = false
  }
}

const showAddDialog = () => {
  isEdit.value = false
  Object.assign(form, {
    id: null,
    name: '',
    device_type: 'xFace100',
    ip_address: '',
    port: 4370,
    location: '',
    serial_number: ''
  })
  dialogVisible.value = true
}

const editDevice = (row) => {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    name: row.name,
    device_type: row.device_type,
    ip_address: row.ip_address,
    port: row.port,
    location: row.location,
    serial_number: row.serial_number || ''
  })
  dialogVisible.value = true
}

const submitForm = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    if (isEdit.value) {
      await updateDevice(form.id, form)
      ElMessage.success('设备已更新')
    } else {
      await createDevice(form)
      ElMessage.success('设备已添加')
    }
    dialogVisible.value = false
    fetchDevices()
  } catch (e) {
    console.error('提交失败', e)
    ElMessage.error(e.response?.data?.detail || (isEdit.value ? '更新失败' : '添加失败'))
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定删除设备 "' + row.name + '"？', '确认删除', { type: 'warning' })
    .then(async () => {
      try {
        await deleteDevice(row.id)
        ElMessage.success('删除成功')
        fetchDevices()
      } catch (e) {
        ElMessage.error('删除失败')
      }
    }).catch(() => {})
}

const checkStatus = async (device) => {
  device.checking = true
  try {
    const res = await checkDeviceStatus(device.id)
    // 直接更新设备状态，不重新加载整个列表
    device.status = res.status
    device.user_count = res.user_count
    device.record_count = res.record_count
    device.firmware_version = res.firmware_version
    device.device_time = res.device_time
    ElMessage.success(res.status === 'online' ? '设备在线' : '设备离线')
  } catch (e) {
    device.status = 'offline'
    ElMessage.error('检测失败')
  } finally {
    device.checking = false
  }
}

const syncDeviceData = async (device) => {
  device.syncing = true
  try {
    await syncDevice(device.id)
    ElMessage.success('同步任务已启动')
  } catch (e) {
    ElMessage.error('同步失败')
  } finally {
    device.syncing = false
  }
}

const downloadDeviceRecords = async (device) => {
  device.downloading = true
  try {
    const res = await downloadRecords(device.id)
    ElMessage.success(`成功下载 ${res.record_count} 条打卡记录`)
    // 更新最后同步时间
    device.last_sync = new Date().toLocaleString()
  } catch (e) {
    ElMessage.error('下载打卡记录失败')
  } finally {
    device.downloading = false
  }
}

onMounted(fetchDevices)
</script>

<style scoped>
.devices-page { padding: 0; }
.search-card { margin-bottom: 0; }
.device-card { margin-bottom: 16px; }
.device-card.offline { opacity: 0.7; }
.device-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.device-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #ec6921 0%, #f0884a 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}
.device-info { flex: 1; }
.device-name { font-size: 16px; font-weight: 600; color: #333; }
.device-type { font-size: 12px; color: #999; margin-top: 2px; }
.device-body { margin-bottom: 16px; }
.device-detail {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
}
.device-detail:last-child { border-bottom: none; }
.device-detail .label { color: #999; font-size: 13px; }
.device-detail .value { color: #333; font-size: 13px; font-weight: 500; }
.device-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
