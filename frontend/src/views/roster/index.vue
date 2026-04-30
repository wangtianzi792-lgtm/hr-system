<template>
  <div class="page-container">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input v-model="searchQuery" placeholder="搜索工号/姓名" clearable @keyup.enter="loadRoster" />
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterDept" placeholder="按部门筛选" clearable>
            <el-option v-for="d in deptList" :key="d" :label="d" :value="d" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="loadRoster" style="background-color:#ec6921;border-color:#ec6921">
            查询
          </el-button>
        </el-col>
        <el-col :span="8" style="text-align:right">
          <span style="font-size:14px;color:#666">花名册共 {{ total }} 人</span>
        </el-col>
      </el-row>
    </el-card>

    <!-- 表格 -->
    <el-card>
      <el-table :data="rosterList" v-loading="loading" stripe style="width:100%">
        <el-table-column prop="工号" label="工号" min-width="100" />
        <el-table-column prop="姓名" label="姓名" min-width="80" />
        <el-table-column prop="部门" label="部门" min-width="140" />
        <el-table-column prop="岗位" label="岗位" min-width="100" />
        <el-table-column prop="职务级别" label="职务级别" min-width="80" />
        <el-table-column prop="用工形式" label="用工形式" min-width="80" />
        <el-table-column prop="公积金标准" label="公积金标准" min-width="100">
          <template #default="scope">
            <span v-if="scope.row.公积金标准" :class="providentClass(scope.row.公积金标准)">
              {{ scope.row.公积金标准 }}
            </span>
            <span v-else style="color:#999">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="入职时间" label="入职时间" min-width="110" />
        <el-table-column prop="联系电话" label="联系电话" min-width="120" />
      </el-table>

      <!-- 分页 -->
      <div style="margin-top:16px;display:flex;justify-content:flex-end">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[50,100,200]"
          layout="total,sizes,prev,pager,next"
          @current-change="loadRoster"
          @size-change="loadRoster"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRosterList } from '@/api/roster'
import { ElMessage } from 'element-plus'

const rosterList = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(100)
const loading = ref(false)
const searchQuery = ref('')
const filterDept = ref('')
const deptList = ref([])

const providentClass = (val) => {
  if (val === '不缴纳' || val === '试用期') return 'provident-warn'
  return ''
}

const loadRoster = async () => {
  loading.value = true
  try {
    const res = await getRosterList({
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchQuery.value || undefined,
      department: filterDept.value || undefined,
    })
    rosterList.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    ElMessage.error('加载花名册失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRoster()
})
</script>

<style scoped>
.provident-warn {
  color: #e6a23c;
}
</style>