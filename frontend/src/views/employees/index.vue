<template>
  <div class="employees-page">
    <!-- 搜索和操作栏 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="5">
          <el-input
            v-model="searchQuery"
            placeholder="搜索姓名/工号/手机号"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button @click="handleSearch">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterDepartment" placeholder="选择部门" clearable @change="handleSearch">
            <el-option
              v-for="dept in departmentList"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterFactory" placeholder="选择厂区" clearable @change="handleSearch">
            <el-option label="二厂" value="二厂" />
            <el-option label="三厂" value="三厂" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterPersonType" placeholder="人员类别" clearable @change="handleSearch">
            <el-option v-for="pt in personTypeOptions" :key="pt" :label="pt" :value="pt" />
          </el-select>
        </el-col>
        <el-col :span="7" style="text-align: right;">
          <el-button type="primary" @click="showAddDialog" style="background-color: #ec6921; border-color: #ec6921;">
            <el-icon><Plus /></el-icon>新增员工
          </el-button>
          <el-button @click="refreshList" style="color: #ec6921; border-color: #ec6921;">
            <el-icon><Refresh /></el-icon>刷新
          </el-button>
          <el-button type="success" @click="exportData">
            <el-icon><Download /></el-icon>导出
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 员工列表 -->
    <el-card style="margin-top: 20px;">
      <el-table :data="employeeList" v-loading="loading" style="width: 100%" stripe>
        <el-table-column type="expand">
          <template #default="scope">
            <el-descriptions :column="3" border size="small">
              <el-descriptions-item label="档案号">{{ scope.row.archive_no || '-' }}</el-descriptions-item>
              <el-descriptions-item label="厂区">{{ scope.row.factory || '-' }}</el-descriptions-item>
              <el-descriptions-item label="事业部">{{ scope.row.business_unit || '-' }}</el-descriptions-item>
              <el-descriptions-item label="职务级别">{{ scope.row.job_level || '-' }}</el-descriptions-item>
              <el-descriptions-item label="试用到期">{{ scope.row.probation_end_date || '-' }}</el-descriptions-item>
              <el-descriptions-item label="紧急电话">{{ scope.row.emergency_phone || '-' }}</el-descriptions-item>
              <el-descriptions-item label="出生日期">{{ getBirthDateFromIdCard(scope.row.id_card) || scope.row.birth_date || '-' }}</el-descriptions-item>
              <el-descriptions-item label="年龄">{{ calculateAgeFromIdCard(scope.row.id_card) || scope.row.age || '-' }}</el-descriptions-item>
              <el-descriptions-item label="性别">{{ formatGender(getGenderFromIdCard(scope.row.id_card) || scope.row.gender) }}</el-descriptions-item>
              <el-descriptions-item label="民族">{{ scope.row.ethnicity || '-' }}</el-descriptions-item>
              <el-descriptions-item label="工龄">{{ calculateWorkYears(scope.row.contract_start) }}</el-descriptions-item>
              <el-descriptions-item label="用工形式">{{ scope.row.employment_type || '-' }}</el-descriptions-item>
              <el-descriptions-item label="文化程度">{{ scope.row.education || '-' }}</el-descriptions-item>
              <el-descriptions-item label="学历工资">{{ scope.row.education_salary || '-' }}</el-descriptions-item>
              <el-descriptions-item label="毕业院校及专业">{{ scope.row.school_major || '-' }}</el-descriptions-item>
              <el-descriptions-item label="户籍地址">{{ scope.row.household_address || '-' }}</el-descriptions-item>
              <el-descriptions-item label="暂住地">{{ scope.row.temporary_address || '-' }}</el-descriptions-item>
              <el-descriptions-item label="合同起始">{{ scope.row.contract_start || '-' }}</el-descriptions-item>
              <el-descriptions-item label="合同终止">{{ scope.row.contract_end || '-' }}</el-descriptions-item>
              <el-descriptions-item label="签定">{{ scope.row.contract_signed || '-' }}</el-descriptions-item>
              <el-descriptions-item label="公积金标准">{{ scope.row.provident_fund || '-' }}</el-descriptions-item>
              <el-descriptions-item label="工龄工资">{{ calculateWorkYearsSalary(scope.row.contract_start) }}</el-descriptions-item>
            </el-descriptions>
          </template>
        </el-table-column>
        <el-table-column prop="employee_no" label="工号" width="100" sortable />
        <el-table-column prop="name" label="姓名" width="140">
          <template #default="scope">
            {{ scope.row.name }}
            <el-tag v-if="scope.row.入职次数 > 1" type="warning" size="small" style="margin-left: 4px;">
              第{{ scope.row.入职次数 }}次入职
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="gender" label="性别" width="70">
          <template #default="scope">
            {{ formatGender(getGenderFromIdCard(scope.row.id_card) || scope.row.gender) }}
          </template>
        </el-table-column>
        <el-table-column label="部门" min-width="120">
          <template #default="scope">{{ scope.row.department_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="person_type" label="人员类别" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.person_type === '正式工'" type="success" size="small">正式工</el-tag>
            <el-tag v-else-if="scope.row.person_type === '劳务工'" type="warning" size="small">劳务工</el-tag>
            <el-tag v-else type="info" size="small">{{ scope.row.person_type || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="factory" label="厂区" width="80" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="id_card" label="身份证号" width="170">
          <template #default="scope">
            {{ maskIdCard(scope.row.id_card) }}
          </template>
        </el-table-column>
        <el-table-column prop="entry_date" label="入职日期" width="110">
          <template #default="scope">
            {{ scope.row.entry_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'" size="small">
              {{ scope.row.status === 'active' ? '在职' : '离职' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="zk_user_id" label="考勤机" width="90">
          <template #default="scope">
            <el-tag v-if="scope.row.zk_user_id" type="success" size="small">已下发</el-tag>
            <el-tag v-else type="info" size="small">未下发</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="scope">
            <el-popover
              placement="left"
              :width="180"
              trigger="click"
              popper-class="operation-popover"
            >
              <template #reference>
                <el-button size="small" style="color: #ec6921;">
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
              </template>
              <div class="operation-menu">
                <div class="operation-item" @click="editEmployee(scope.row)">
                  <el-icon><Edit /></el-icon> 编辑
                </div>
                <div class="operation-item" @click="enrollDevice(scope.row)">
                  <el-icon><Download /></el-icon> 下发到考勤机
                </div>
                <div class="operation-item" @click="removeDevice(scope.row)">
                  <el-icon><Upload /></el-icon> 从考勤机移除
                </div>
                <el-divider style="margin: 8px 0;" />
                <div class="operation-item delete" @click="handleDelete(scope.row)">
                  <el-icon><Delete /></el-icon> 删除
                </div>
              </div>
            </el-popover>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[50, 100, 500, 1000]"
        layout="total, sizes, prev, pager, next"
        style="margin-top: 20px; justify-content: flex-end;"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <!-- 新增/编辑员工对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑员工' : '新增员工'"
      width="850px"
      top="5vh"
    >
      <el-form :model="employeeForm" :rules="rules" ref="employeeFormRef" label-width="110px">
        <el-scrollbar max-height="600px">
          <el-divider content-position="left">基本信息</el-divider>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="工号" prop="employee_no">
                <el-input v-model="employeeForm.employee_no" placeholder="请输入工号" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="姓名" prop="name">
                <el-input v-model="employeeForm.name" placeholder="请输入姓名" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="性别" prop="gender">
                <el-input :value="formatGender(getGenderFromIdCard(employeeForm.id_card) || employeeForm.gender)" disabled placeholder="根据身份证号自动识别" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="部门" prop="department_id">
                <el-select v-model="employeeForm.department_id" placeholder="请选择部门" style="width: 100%" @change="onDepartmentChange">
                  <el-option
                    v-for="dept in departmentList"
                    :key="dept.id"
                    :label="dept.name"
                    :value="dept.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="职位" prop="position">
                <el-select v-model="employeeForm.position" placeholder="选择职位（职位决定系统权限）" style="width: 100%" @change="onPositionChange">
                  <el-option v-for="role in roleList" :key="role.id" :label="role.display_name" :value="role.display_name" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="系统角色">
                <el-input :model-value="getRoleDisplay(employeeForm.role_id)" placeholder="由职位自动决定" disabled />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="人员类别">
                <el-select v-model="employeeForm.person_type" placeholder="请选择" style="width: 100%">
                  <el-option label="正式工" value="正式工" />
                  <el-option label="劳务工" value="劳务工" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="厂区">
                <el-select v-model="employeeForm.factory" placeholder="请选择" style="width: 100%">
                  <el-option label="二厂" value="二厂" />
                  <el-option label="三厂" value="三厂" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="事业部">
                <el-input v-model="employeeForm.business_unit" placeholder="请输入事业部" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="手机号" prop="phone">
                <el-input v-model="employeeForm.phone" placeholder="请输入手机号" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="身份证号">
                <el-input v-model="employeeForm.id_card" placeholder="请输入身份证号" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="档案号">
                <el-input v-model="employeeForm.archive_no" placeholder="请输入档案号" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-divider content-position="left">工作信息</el-divider>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="入职日期" prop="entry_date">
                <el-date-picker
                  v-model="employeeForm.entry_date"
                  type="date"
                  placeholder="选择日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="试用到期日">
                <el-date-picker
                  v-model="employeeForm.probation_end_date"
                  type="date"
                  placeholder="选择日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="职务级别">
                <el-input v-model="employeeForm.job_level" placeholder="请输入职务级别" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="工龄">
                <el-input :value="calculateWorkYears(employeeForm.contract_start)" disabled placeholder="自动计算" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="用工形式">
                <el-select v-model="employeeForm.employment_type" placeholder="请选择" style="width: 100%">
                  <el-option label="合同制" value="合同制" />
                  <el-option label="劳务派遣" value="劳务派遣" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-divider content-position="left">联系信息</el-divider>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="紧急电话">
                <el-input v-model="employeeForm.emergency_phone" placeholder="请输入紧急联系电话" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="户籍地址">
                <el-input v-model="employeeForm.household_address" placeholder="请输入户籍地址" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="暂住地">
                <el-input v-model="employeeForm.temporary_address" placeholder="请输入扬州暂住地" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-divider content-position="left">合同与薪酬</el-divider>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="合同起始">
                <el-date-picker
                  v-model="employeeForm.contract_start"
                  type="date"
                  placeholder="选择日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="合同终止">
                <el-date-picker
                  v-model="employeeForm.contract_end"
                  type="date"
                  placeholder="选择日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="签定">
                <el-input v-model="employeeForm.contract_signed" placeholder="请输入签定次数" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="公积金标准">
                <el-input v-model="employeeForm.provident_fund" placeholder="请输入公积金标准" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="工龄工资">
                <el-input :value="calculateWorkYearsSalary(employeeForm.contract_start)" disabled placeholder="根据工龄自动计算" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="学历工资">
                <el-input :value="getEducationSalary(employeeForm.education)" disabled placeholder="根据学历自动计算" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-divider content-position="left">其他信息</el-divider>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="文化程度">
                <el-select v-model="employeeForm.education" placeholder="请选择" style="width: 100%">
                  <el-option label="初中" value="初中" />
                  <el-option label="高中" value="高中" />
                  <el-option label="中专" value="中专" />
                  <el-option label="大专" value="大专" />
                  <el-option label="本科" value="本科" />
                  <el-option label="硕士" value="硕士" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="毕业院校及专业">
                <el-input v-model="employeeForm.school_major" placeholder="请输入毕业院校及专业" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="民族">
                <el-input v-model="employeeForm.ethnicity" placeholder="请输入民族" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="出生日期">
                <el-input :value="getBirthDateFromIdCard(employeeForm.id_card) || employeeForm.birth_date" disabled placeholder="根据身份证号自动计算" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="状态" prop="status">
            <el-radio-group v-model="employeeForm.status">
              <el-radio label="active">在职</el-radio>
              <el-radio label="leave">离职</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-scrollbar>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitLoading" style="background-color: #ec6921; border-color: #ec6921;">
          {{ isEdit ? '保存' : '新增' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 下发到考勤机对话框 -->
    <el-dialog v-model="enrollDialogVisible" title="下发到考勤机" width="400px">
      <el-form label-width="100px">
        <el-form-item label="选择设备">
          <el-select v-model="selectedDevice" placeholder="请选择考勤机" style="width: 100%">
            <el-option
              v-for="device in deviceList"
              :key="device.id"
              :label="device.name"
              :value="device.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="enrollDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmEnroll" :loading="enrollLoading" style="background-color: #ec6921; border-color: #ec6921;">
          确认下发
        </el-button>
      </template>
    </el-dialog>

    <!-- 从考勤机移除对话框 -->
    <el-dialog v-model="removeDialogVisible" title="从考勤机移除" width="400px">
      <el-form label-width="100px">
        <el-form-item label="选择设备">
          <el-select v-model="selectedDevice" placeholder="请选择考勤机" style="width: 100%">
            <el-option
              v-for="device in deviceList"
              :key="device.id"
              :label="device.name"
              :value="device.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="removeDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmRemove" :loading="removeLoading">
          确认移除
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getEmployees, createEmployee, updateEmployee, deleteEmployee, deployToDevice, removeFromDevice } from '@/api/employees'
import { getDepartments } from '@/api/departments'
import { getDevices } from '@/api/devices'
import { getRoles } from '@/api/roles'
import { exportEmployees } from '@/utils/export'
import { MoreFilled, Edit, Download, Upload, Delete } from '@element-plus/icons-vue'

// Data
const employeeList = ref([])
const departmentList = ref([])
const deviceList = ref([])
const roleList = ref([])
const loading = ref(false)
const searchQuery = ref('')
const filterDepartment = ref('')
const filterFactory = ref('')
const filterPersonType = ref('')
const personTypeOptions = ['正式工', '劳务工']
const currentPage = ref(1)
const pageSize = ref(100)
const total = ref(0)

// Dialog
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const employeeFormRef = ref(null)

const employeeForm = reactive({
  id: null,
  employee_no: '',
  name: '',
  gender: '',
  phone: '',
  email: '',
  id_card: '',
  department_id: '',
  department_name: '',
  position: '',
  role_id: null,
  entry_date: '',
  card_no: '',
  status: 'active',
  // 扩展字段
  archive_no: '',
  factory: '',
  person_type: '',
  business_unit: '',
  process: '',
  job_level: '',
  probation_end_date: '',
  emergency_phone: '',
  birth_date: '',
  age: null,
  ethnicity: '',
  work_years: '',
  employment_type: '',
  medical_category: '',
  employee_group: '',
  education: '',
  education_salary: '',
  school_major: '',
  household_address: '',
  temporary_address: '',
  contract_start: '',
  contract_end: '',
  contract_signed: '',
  provident_fund: '',
  work_years_salary: '',
  training: ''
})

const rules = {
  employee_no: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  department_id: [{ required: true, message: '请选择部门', trigger: 'change' }]
}

// Deploy dialog
const enrollDialogVisible = ref(false)
const enrollLoading = ref(false)
const removeDialogVisible = ref(false)
const removeLoading = ref(false)
const selectedDevice = ref('')
const currentEmployee = ref(null)

// Methods
const formatGender = (gender) => {
  if (gender === 'M' || gender === 'male' || gender === '男') return '男'
  if (gender === 'F' || gender === 'female' || gender === '女') return '女'
  return '-'
}

const calculateWorkYears = (contractStart) => {
  if (!contractStart) return '-'
  const start = new Date(contractStart)
  const now = new Date()
  const years = now.getFullYear() - start.getFullYear()
  return years > 0 ? years + '年' : '不足1年'
}

const calculateWorkYearsSalary = (contractStart) => {
  if (!contractStart) return '-'
  const start = new Date(contractStart)
  const now = new Date()
  const years = now.getFullYear() - start.getFullYear()
  if (years <= 0) return '0元'
  const salary = Math.min(years * 50, 500)
  return salary + '元'
}

const getGenderFromIdCard = (idCard) => {
  if (!idCard || idCard.length !== 18) return null
  const genderCode = parseInt(idCard.substring(16, 17))
  return genderCode % 2 === 1 ? 'male' : 'female'
}

const getBirthDateFromIdCard = (idCard) => {
  if (!idCard || idCard.length !== 18) return null
  const year = idCard.substring(6, 10)
  const month = idCard.substring(10, 12)
  const day = idCard.substring(12, 14)
  return year + '-' + month + '-' + day
}

const calculateAgeFromIdCard = (idCard) => {
  if (!idCard || idCard.length !== 18) return null
  const birthYear = parseInt(idCard.substring(6, 10))
  const birthMonth = parseInt(idCard.substring(10, 12))
  const birthDay = parseInt(idCard.substring(12, 14))
  const now = new Date()
  let age = now.getFullYear() - birthYear
  const monthDiff = now.getMonth() + 1 - birthMonth
  const dayDiff = now.getDate() - birthDay
  if (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)) {
    age--
  }
  return age > 0 ? age : 0
}

const getEducationSalary = (education) => {
  const salaryMap = {
    '初中': '0元',
    '初中及以下': '0元',
    '高中': '100元',
    '中专': '100元',
    '大专': '300元',
    '本科': '500元',
    '硕士': '800元'
  }
  return salaryMap[education] || '-'
}

const maskIdCard = (idCard) => {
  if (!idCard || idCard.length !== 18) return idCard || '-'
  return idCard.substring(0, 6) + '********' + idCard.substring(14)
}

const fetchEmployees = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      ...(searchQuery.value && { keyword: searchQuery.value }),
      ...(filterDepartment.value && { department_id: filterDepartment.value }),
      ...(filterFactory.value && { factory: filterFactory.value }),
      ...(filterPersonType.value && { person_type: filterPersonType.value })
    }
    const res = await getEmployees(params)
    employeeList.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('获取员工列表失败:', error)
    ElMessage.error('获取员工列表失败')
  } finally {
    loading.value = false
  }
}

const fetchDepartments = async () => {
  try {
    const res = await getDepartments({ limit: 100 })
    departmentList.value = Array.isArray(res) ? res : (res.items || [])
  } catch (error) {
    console.error('获取部门列表失败:', error)
  }
}

const fetchDevices = async () => {
  try {
    const res = await getDevices({ limit: 100 })
    deviceList.value = res.items || []
  } catch (error) {
    console.error('获取设备列表失败:', error)
  }
}

const fetchRoles = async () => {
  try {
    const res = await getRoles()
    roleList.value = res || []
  } catch (error) {
    console.error('获取角色列表失败:', error)
  }
}

// 职位变更时自动设置角色
function onPositionChange(positionName) {
  const role = roleList.value.find(r => r.display_name === positionName)
  employeeForm.role_id = role ? role.id : null
}

// 部门变更时更新名称
function onDepartmentChange(deptId) {
  const dept = departmentList.value.find(d => d.id === deptId)
  employeeForm.department_name = dept ? dept.name : ''
}

// 获取角色显示名
function getRoleDisplay(roleId) {
  if (!roleId) return '-'
  const role = roleList.value.find(r => r.id === roleId)
  return role ? role.display_name : '-'
}

const handleSearch = () => {
  currentPage.value = 1
  fetchEmployees()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchEmployees()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchEmployees()
}

const refreshList = () => {
  searchQuery.value = ''
  filterDepartment.value = ''
  filterFactory.value = ''
  filterPersonType.value = ''
  currentPage.value = 1
  fetchEmployees()
}

const exportData = () => {
  if (employeeList.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }
  
  const exportData = employeeList.value.map(row => ({
    employee_no: row.employee_no,
    name: row.name,
    gender: formatGender(getGenderFromIdCard(row.id_card) || row.gender),
    department_name: row.department_name,
    position: row.position,
    person_type: row.person_type,
    factory: row.factory,
    phone: row.phone,
    id_card: row.id_card,
    entry_date: row.entry_date || '-',
    archive_no: row.archive_no,
    business_unit: row.business_unit,
    process: row.process,
    job_level: row.job_level,
    probation_end_date: row.probation_end_date,
    emergency_phone: row.emergency_phone,
    birth_date: getBirthDateFromIdCard(row.id_card) || row.birth_date,
    age: calculateAgeFromIdCard(row.id_card) || row.age,
    ethnicity: row.ethnicity,
    work_years: row.work_years,
    employment_type: row.employment_type,
    medical_category: row.medical_category,
    employee_group: row.employee_group,
    education: row.education,
    education_salary: row.education_salary,
    school_major: row.school_major,
    household_address: row.household_address,
    temporary_address: row.temporary_address,
    contract_start: row.contract_start,
    contract_end: row.contract_end,
    contract_signed: row.contract_signed,
    provident_fund: row.provident_fund,
    work_years_salary: calculateWorkYearsSalary(row.contract_start),
    training: row.training,
    status: row.status === 'active' ? '在职' : '离职'
  }))
  
  exportEmployees(exportData)
  ElMessage.success('导出成功')
}

const showAddDialog = () => {
  isEdit.value = false
  Object.assign(employeeForm, {
    id: null,
    employee_no: '',
    name: '',
    gender: '',
    phone: '',
    email: '',
    id_card: '',
    department_id: '',
    department_name: '',
    position: '',
    entry_date: '',
    card_no: '',
    status: 'active',
    archive_no: '',
    factory: '',
    person_type: '',
    business_unit: '',
    process: '',
    job_level: '',
    probation_end_date: '',
    emergency_phone: '',
    birth_date: '',
    age: null,
    ethnicity: '',
    work_years: '',
    employment_type: '',
    medical_category: '',
    employee_group: '',
    education: '',
    education_salary: '',
    school_major: '',
    household_address: '',
    temporary_address: '',
    contract_start: '',
    contract_end: '',
    contract_signed: '',
    provident_fund: '',
    work_years_salary: '',
    training: ''
  })
  dialogVisible.value = true
}

const editEmployee = (row) => {
  isEdit.value = true
  Object.assign(employeeForm, row)
  // 编辑时，职位显示为角色名
  if (row.role_name) {
    employeeForm.position = row.role_name
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  const valid = await employeeFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    // 自动根据职位匹配角色
    if (employeeForm.position) {
      const matchedRole = roleList.value.find(r => r.display_name === employeeForm.position)
      if (matchedRole) {
        employeeForm.role_id = matchedRole.id
      }
    }

    if (isEdit.value) {
      await updateEmployee(employeeForm.id, employeeForm)
      ElMessage.success('员工更新成功')
    } else {
      await createEmployee(employeeForm)
      ElMessage.success('员工新增成功')
    }
    dialogVisible.value = false
    fetchEmployees()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(isEdit.value ? '更新失败' : '新增失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除员工 "' + row.name + '" 吗？', '确认删除', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteEmployee(row.id)
      ElMessage.success('删除成功')
      fetchEmployees()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const enrollDevice = (row) => {
  currentEmployee.value = row
  selectedDevice.value = ''
  enrollDialogVisible.value = true
}

const confirmEnroll = async () => {
  if (!selectedDevice.value) {
    ElMessage.warning('请选择设备')
    return
  }
  
  enrollLoading.value = true
  try {
    await deployToDevice(currentEmployee.value.id, selectedDevice.value)
    ElMessage.success('员工下发到考勤机成功')
    enrollDialogVisible.value = false
    fetchEmployees()
  } catch (error) {
    console.error('下发失败:', error)
    ElMessage.error('下发失败')
  } finally {
    enrollLoading.value = false
  }
}

const removeDevice = (row) => {
  currentEmployee.value = row
  selectedDevice.value = ''
  removeDialogVisible.value = true
}

const confirmRemove = async () => {
  if (!selectedDevice.value) {
    ElMessage.warning('请选择设备')
    return
  }
  
  removeLoading.value = true
  try {
    await removeFromDevice(currentEmployee.value.id, selectedDevice.value)
    ElMessage.success('员工已从考勤机移除')
    removeDialogVisible.value = false
    fetchEmployees()
  } catch (error) {
    console.error('移除失败:', error)
    ElMessage.error('移除失败')
  } finally {
    removeLoading.value = false
  }
}

onMounted(() => {
  fetchEmployees()
  fetchDepartments()
  fetchDevices()
  fetchRoles()
})
</script>

<style scoped>
.employees-page {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.operation-menu {
  padding: 4px 0;
}

.operation-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  transition: background-color 0.2s;
}

.operation-item:hover {
  background-color: #f5f7fa;
  color: #ec6921;
}

.operation-item .el-icon {
  margin-right: 8px;
  font-size: 16px;
}

.operation-item.delete {
  color: #f56c6c;
}

.operation-item.delete:hover {
  background-color: #fef0f0;
  color: #f56c6c;
}
</style>
