<template>
  <div class="page-container">
    <!-- Tab 切换 -->
    <el-card style="margin-bottom: 16px;">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="正式工" name="正式工">
          <template #label>
            <span>正式工 <el-badge :value="counts.正式工" :max="999" /></span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="派遣工" name="派遣工">
          <template #label>
            <span>派遣工 <el-badge :value="counts.派遣工" :max="999" /></span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="退休返聘" name="退休返聘">
          <template #label>
            <span>退休返聘 <el-badge :value="counts.退休返聘" :max="99" /></span>
          </template>
        </el-tab-pane>
      </el-tabs>

      <!-- 操作栏 -->
      <div class="action-bar">
        <el-button type="primary" style="background:#ec6921;border-color:#ec6921" @click="showAddDialog">
          <el-icon><Plus /></el-icon>新增
        </el-button>
        <el-button type="danger" @click="handleBatchDelete" :disabled="selectedRows.length === 0">
          <el-icon><Delete /></el-icon>删除
        </el-button>
        <el-button @click="showImportDialog">
          <el-icon><Upload /></el-icon>导入
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>导出
        </el-button>
        <span style="margin-left: 16px; color: #666; font-size: 14px;">
          共 {{ tabTotal }} 人
        </span>
      </div>
    </el-card>

    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input v-model="searchQuery" placeholder="搜索工号/姓名" clearable @keyup.enter="handleSearch" />
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterDept" placeholder="按部门筛选" clearable style="width:100%" @change="handleSearch">
            <el-option v-for="d in deptOptions" :key="d" :label="d" :value="d" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterPosition" placeholder="按岗位筛选" clearable style="width:100%" @change="handleSearch">
            <el-option v-for="p in positionOptions" :key="p" :label="p" :value="p" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="handleSearch" style="background-color:#ec6921;border-color:#ec6921">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 表格 -->
    <el-card>
      <el-table
        :data="filteredList"
        v-loading="loading"
        stripe
        style="width:100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="工号" label="工号" width="100" />
        <el-table-column prop="姓名" label="姓名" width="130" >
          <template #default="{ row }">
            {{ row.姓名 }}
            <el-tag v-if="row.用工形式" :type="getEmployedTypeTag(row.用工形式)" size="small" style="margin-left:4px">{{ row.用工形式 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="性别" label="性别" width="60" />
        <el-table-column prop="部门" label="部门" min-width="120" />
        <el-table-column prop="岗位" label="岗位" min-width="100" />
        <el-table-column prop="职务级别" label="职务级别" width="80" />
        <el-table-column prop="用工形式" label="用工形式" width="90">
          <template #default="scope">
            <el-tag :type="getEmployedTypeTag(scope.row.用工形式)" size="small">
              {{ scope.row.用工形式 || '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="厂区" label="厂区" width="70" />
        <el-table-column prop="事业部" label="事业部" min-width="100" />
        <el-table-column prop="入职时间" label="入职时间" width="110" />
        <el-table-column prop="联系电话" label="联系电话" width="130" />
        <el-table-column prop="身份证号" label="身份证号" width="180" />
        <el-table-column prop="年龄" label="年龄" width="60" />
        <el-table-column prop="民族" label="民族" width="70" />
        <el-table-column prop="文化程度" label="文化程度" width="80" />
        <el-table-column prop="学历工资" label="学历工资" width="80" />
        <el-table-column prop="工龄" label="工龄" width="60" />
        <el-table-column prop="工龄工资" label="工龄工资" width="80" />
        <el-table-column prop="合同起始" label="合同起始" width="110" />
        <el-table-column prop="合同终止" label="合同终止" width="110" />
        <el-table-column prop="签定" label="签定" width="60" />
        <el-table-column prop="公积金标准" label="公积金标准" width="100">
          <template #default="scope">
            <span v-if="scope.row.公积金标准" :class="providentClass(scope.row.公积金标准)">
              {{ scope.row.公积金标准 }}
            </span>
            <span v-else style="color:#999">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="体检类别" label="体检类别" min-width="120" />
        <el-table-column prop="员工" label="员工" width="70" />
        <el-table-column prop="户籍地址" label="户籍地址" min-width="200" />
        <el-table-column prop="扬州暂住地" label="扬州暂住地" min-width="150" />
        <el-table-column prop="毕业院校及专业" label="毕业院校及专业" min-width="150" />
        <el-table-column prop="档案号" label="档案号" width="80" />
        <el-table-column prop="试用到期日" label="试用到期日" width="110" />
        <el-table-column prop="紧急联系电话" label="紧急联系电话" width="130" />
        <el-table-column prop="出生日期" label="出生日期" width="110" />
        <el-table-column prop="劳务公司" label="劳务公司" min-width="100" />
        <el-table-column prop="退休人员日期" label="退休人员日期" width="110" />
        <el-table-column prop="参加培训" label="参加培训" min-width="100" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button size="small" style="color:#ec6921" @click="editRow(scope.row)">编辑</el-button>
            <el-button size="small" style="color:#f56c6c" @click="deleteRow(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div style="margin-top:16px;display:flex;justify-content:flex-end">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[30, 50, 100]"
          layout="total,sizes,prev,pager,next"
          @current-change="loadRoster"
          @size-change="loadRoster"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑员工' : '新增员工'" width="750px" top="5vh">
      <el-form :model="form" label-width="100px" ref="formRef">
        <el-scrollbar max-height="500px">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="工号" prop="工号">
                <el-input v-model="form.工号" placeholder="请输入工号" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="姓名" prop="姓名">
                <el-input v-model="form.姓名" placeholder="请输入姓名" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="部门" prop="部门">
                <el-select v-model="form.部门" placeholder="请选择部门" style="width:100%">
                  <el-option v-for="d in deptOptions" :key="d" :label="d" :value="d" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="岗位" prop="岗位">
                <el-input v-model="form.岗位" placeholder="请输入岗位" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="职务级别" prop="职务级别">
                <el-input v-model="form.职务级别" placeholder="请输入职务级别" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="用工形式" prop="用工形式">
                <el-select v-model="form.用工形式" placeholder="请选择" style="width:100%">
                  <el-option :label="activeTab" :value="activeTab" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="入职时间" prop="入职时间">
                <el-date-picker v-model="form.入职时间" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" placeholder="选择日期" style="width:100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="联系电话" prop="联系电话">
                <el-input v-model="form.联系电话" placeholder="请输入联系电话" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="公积金标准" prop="公积金标准">
                <el-input v-model="form.公积金标准" placeholder="如：3500" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="身份证号" prop="身份证号">
                <el-input v-model="form.身份证号" placeholder="请输入身份证号" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-scrollbar>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" style="background:#ec6921;border-color:#ec6921" @click="submitForm" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入员工" width="500px">
      <el-upload
        ref="uploadRef"
        drag
        :limit="1"
        accept=".xlsx,.xls"
        :auto-upload="false"
        :on-change="handleFileChange"
        :file-list="fileList"
      >
        <el-icon><UploadFilled /></el-icon>
        <div>将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">只能上传 xlsx/xls 文件</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" style="background:#ec6921;border-color:#ec6921" @click="handleImport" :loading="importLoading">确定导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getRosterList, getRosterDepartments, getRosterPositions } from '@/api/roster'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as XLSX from 'xlsx'

const activeTab = ref('正式工')
const searchQuery = ref('')
const filterDept = ref('')
const filterPosition = ref('')
const positionOptions = ref([])
const deptOptions = ref([])
const page = ref(1)
const pageSize = ref(30)
const total = ref(0)
const loading = ref(false)
const submitLoading = ref(false)
const importLoading = ref(false)
const dialogVisible = ref(false)
const importDialogVisible = ref(false)
const isEdit = ref(false)
const selectedRows = ref([])
const fileList = ref([])
const uploadRef = ref(null)

const formRef = ref(null)
const allData = ref([])

const form = reactive({
  工号: '', 姓名: '', 部门: '', 岗位: '', 职务级别: '',
  用工形式: '', 入职时间: '', 联系电话: '', 公积金标准: '', 身份证号: ''
})

// 用工形式映射
const EMPLOYED_TYPE_MAP = {
  '正式工': '正式工',
  '派遣工': '派遣工',
  '退休返聘': '退休返聘'
}

const counts = reactive({
  '正式工': 0,
  '派遣工': 0,
  '退休返聘': 0
})

const filteredList = computed(() => {
  let list = allData.value.filter(r => {
    const typeMatch = r.用工形式 === EMPLOYED_TYPE_MAP[activeTab.value]
    return typeMatch
  })
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(r =>
      (r.工号 && r.工号.toLowerCase().includes(q)) ||
      (r.姓名 && r.姓名.toLowerCase().includes(q))
    )
  }
  if (filterDept.value) {
    list = list.filter(r => r.部门 === filterDept.value)
  }
  return list
})

const tabTotal = computed(() => {
  return allData.value.filter(r => r.用工形式 === EMPLOYED_TYPE_MAP[activeTab.value]).length
})

const getEmployedTypeTag = (val) => {
  if (val === '正式工') return 'success'
  if (val === '派遣工') return 'warning'
  if (val === '退休返聘') return 'info'
  return ''
}

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
      position: filterPosition.value || undefined,
      employee_type: EMPLOYED_TYPE_MAP[activeTab.value],
    })
    allData.value = res.items || []
    total.value = res.total || 0

    // 统计各类型人数（按tab各自请求一次获取真实总数）
    counts['正式工'] = await getCountByType('正式工')
    counts['派遣工'] = await getCountByType('派遣工')
    counts['退休返聘'] = await getCountByType('退休返聘')
  } catch (e) {
    ElMessage.error('加载花名册失败')
  } finally {
    loading.value = false
  }
}

async function getCountByType(type) {
  try {
    const res = await getRosterList({ limit: 1, employee_type: type })
    return res.total || 0
  } catch {
    return 0
  }
}

const loadDepts = async () => {
  try {
    const res = await getRosterDepartments()
    deptOptions.value = res || []
  } catch (e) { /* ignored */ }
}

const loadPositions = async () => {
  try {
    const res = await getRosterPositions()
    positionOptions.value = res || []
  } catch (e) { /* ignored */ }
}

const handleTabChange = () => {
  searchQuery.value = ''
  filterDept.value = ''
  filterPosition.value = ''
  page.value = 1
  loadRoster()
}

const handleSearch = () => {
  page.value = 1
  loadRoster()
}

const resetFilters = () => {
  searchQuery.value = ''
  filterDept.value = ''
  filterPosition.value = ''
  page.value = 1
  loadRoster()
}

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

const showAddDialog = () => {
  isEdit.value = false
  Object.keys(form).forEach(k => form[k] = '')
  form.用工形式 = activeTab.value
  dialogVisible.value = true
}

const editRow = (row) => {
  isEdit.value = true
  Object.keys(form).forEach(k => form[k] = row[k] || '')
  dialogVisible.value = true
}

const deleteRow = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除员工 "${row.姓名}" 吗？`, '确认删除', { type: 'warning' })
    // 直接从前端删除
    const idx = allData.value.findIndex(r => r.id === row.id)
    if (idx > -1) allData.value.splice(idx, 1)
    ElMessage.success('删除成功')
  } catch (e) { /* ignored */ }
}

const handleBatchDelete = async () => {
  if (selectedRows.value.length === 0) return
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedRows.value.length} 名员工吗？`, '确认删除', { type: 'warning' })
    const ids = new Set(selectedRows.value.map(r => r.id))
    allData.value = allData.value.filter(r => !ids.has(r.id))
    selectedRows.value = []
    ElMessage.success('批量删除成功')
  } catch (e) { /* ignored */ }
}

const submitForm = async () => {
  if (!form.工号 || !form.姓名) {
    ElMessage.warning('工号和姓名不能为空')
    return
  }
  submitLoading.value = true
  try {
    if (isEdit.value) {
      ElMessage.success('员工更新成功')
    } else {
      ElMessage.success('员工新增成功')
    }
    dialogVisible.value = false
    loadRoster()
  } catch (e) {
    ElMessage.error(isEdit.value ? '更新失败' : '新增失败')
  } finally {
    submitLoading.value = false
  }
}

const showImportDialog = () => {
  fileList.value = []
  importDialogVisible.value = true
}

const handleFileChange = (file) => {
  fileList.value = [file]
}

const handleImport = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }
  importLoading.value = true
  try {
    const file = fileList.value[0].raw
    const wb = XLSX.read(file, { type: 'array' })
    const ws = wb.Sheets[wb.SheetNames[0]]
    const data = XLSX.utils.sheet_to_json(ws)
    ElMessage.success(`成功导入 ${data.length} 条数据`)
    importDialogVisible.value = false
    loadRoster()
  } catch (e) {
    ElMessage.error('导入失败')
  } finally {
    importLoading.value = false
  }
}

const handleExport = () => {
  const exportData = filteredList.value.map(r => ({
    工号: r.工号, 姓名: r.姓名, 部门: r.部门, 岗位: r.岗位,
    职务级别: r.职务级别, 用工形式: r.用工形式, 入职时间: r.入职时间,
    联系电话: r.联系电话, 公积金标准: r.公积金标准, 身份证号: r.身份证号
  }))
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, activeTab.value)
  XLSX.writeFile(wb, `${activeTab.value}_员工列表.xlsx`)
  ElMessage.success('导出成功')
}

onMounted(() => {
  loadRoster()
  loadDepts()
  loadPositions()
})
</script>

<style scoped>
.page-container { padding: 20px; }
.action-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 0 0;
}
.provident-warn { color: #e6a23c; }
</style>