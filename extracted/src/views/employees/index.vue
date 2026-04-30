<template>
  <div class="employees-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>员工管理</span>
          <span style="font-size:12px;color:#999">共 {{ total }} 人</span>
        </div>
      </template>

      <div style="margin-bottom:16px">
        <el-radio-group v-model="activeTab" @change="handleTabChange" size="default">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="employed">在职</el-radio-button>
          <el-radio-button label="probation">试用</el-radio-button>
          <el-radio-button label="left">离职</el-radio-button>
        </el-radio-group>
      </div>

      <el-row :gutter="20" style="margin-bottom:16px">
        <el-col :span="6">
          <el-input v-model="searchQuery" placeholder="搜索工号/姓名/部门/岗位" clearable @keyup.enter="loadData" />
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterDept" placeholder="按部门筛选" clearable style="width:100%" @change="loadData">
            <el-option v-for="d in deptOptions" :key="d" :label="d" :value="d" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterType" placeholder="人员类别" clearable style="width:100%" @change="loadData">
            <el-option label="正式工" value="正式工" />
            <el-option label="派遣工" value="派遣工" />
            <el-option label="退休返聘" value="退休返聘" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" style="background-color:#ec6921;border-color:#ec6921" @click="loadData">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>

      <el-table :data="filteredList" v-loading="loading" stripe style="width:100%">
        <el-table-column prop="工号" label="工号" width="100" sortable />
        <el-table-column label="姓名" width="150">
          <template #default="{ row }">
            {{ row.姓名 }}
            <el-tag v-if="row.入职次数 && row.入职次数 > 1" type="warning" size="small" style="margin-left:4px">第{{ row.入职次数 }}次入职</el-tag>
            <el-tag v-if="getStatusTag(row) === '试用'" type="warning" size="small" style="margin-left:4px">试用</el-tag>
            <el-tag v-else-if="getStatusTag(row) === '离职'" type="info" size="small" style="margin-left:4px">离职</el-tag>
            <el-tag v-else type="success" size="small" style="margin-left:4px">在职</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="性别" label="性别" width="70" />
        <el-table-column prop="部门" label="部门" min-width="120" />
        <el-table-column prop="岗位" label="岗位" min-width="120" />
        <el-table-column prop="用工形式" label="类别" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.用工形式 === '正式工'" type="success" size="small">正式工</el-tag>
            <el-tag v-else-if="row.用工形式 === '派遣工'" type="warning" size="small">派遣工</el-tag>
            <el-tag v-else type="info" size="small">{{ row.用工形式 || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="职务级别" label="职务级别" width="100" />
        <el-table-column prop="联系电话" label="手机号" width="130" />
        <el-table-column prop="入职时间" label="入职日期" width="110" sortable />
        <el-table-column label="试用到期" width="110">
          <template #default="{ row }">
            <span v-if="row.试用到期日 && row.试用到期日 !== '无'" :style="{ color: isInProbation(row) ? '#e6a23c' : '#999' }">
              {{ row.试用到期日 }}
            </span>
            <span v-else style="color:#999">—</span>
          </template>
        </el-table-column>
        <el-table-column label="入职次数" width="90">
          <template #default="{ row }">
            <span v-if="row.入职次数 && row.入职次数 > 1" style="color:#e6a23c;font-size:12px">第{{ row.入职次数 }}次</span>
            <span v-else style="color:#999">—</span>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getRosterList, getRosterDepartments } from '@/api/roster'

const activeTab = ref('all')
const searchQuery = ref('')
const filterDept = ref('')
const filterType = ref('')
const deptOptions = ref([])
const page = ref(1)
const pageSize = ref(30)
const total = ref(0)
const loading = ref(false)
const allData = ref([])

const isInProbation = (row) => {
  if (!row.试用到期日 || row.试用到期日 === '无') return false
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const probationDate = new Date(row.试用到期日)
  return probationDate >= today
}

const getStatusTag = (row) => {
  if (String(row.是否在职) === '0') return '离职'
  if (isInProbation(row)) return '试用'
  return '在职'
}

const handleTabChange = () => {
  page.value = 1
  loadData()
}

const filteredList = computed(() => {
  let list = allData.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(r =>
      (r.工号 && r.工号.toLowerCase().includes(q)) ||
      (r.姓名 && r.姓名.toLowerCase().includes(q)) ||
      (r.部门 && r.部门.toLowerCase().includes(q)) ||
      (r.岗位 && r.岗位.toLowerCase().includes(q)) ||
      (r.联系电话 && r.联系电话.includes(q))
    )
  }
  if (filterDept.value) list = list.filter(r => r.部门 === filterDept.value)
  if (filterType.value) list = list.filter(r => r.用工形式 === filterType.value)
  return list
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getRosterList({
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchQuery.value || undefined,
      department: filterDept.value || undefined,
      employee_type: filterType.value || undefined,
      status: activeTab.value,
    })
    console.log('[员工管理] API返回数据:', JSON.stringify(res.items ? res.items[0] : 'no data'))
    allData.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  filterDept.value = ''
  filterType.value = ''
  page.value = 1
  loadData()
}

onMounted(() => {
  loadData()
  getRosterDepartments().then(res => { deptOptions.value = res || [] }).catch(() => {})
})
</script>

<style scoped>
.employees-page { padding: 0; }
.card-header { display:flex; justify-content:space-between; align-items:center; }
</style>
