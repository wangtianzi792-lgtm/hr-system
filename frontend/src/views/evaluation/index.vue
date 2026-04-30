<template>
  <div class="evaluation-container">
    <div class="page-header">
      <h2>360考核管理</h2>
      <el-button type="primary" @click="showDialog()">新建考核周期</el-button>
    </div>

    <div class="filter-bar">
      <el-select v-model="query.year" placeholder="年度" clearable style="width:120px" @change="loadCycles">
        <el-option v-for="y in years" :key="y" :label="y+'年'" :value="y"/>
      </el-select>
      <el-select v-model="query.status" placeholder="状态" clearable style="width:120px" @change="loadCycles">
        <el-option label="草稿" value="draft"/><el-option label="进行中" value="active"/>
        <el-option label="已完成" value="completed"/><el-option label="已归档" value="archived"/>
      </el-select>
    </div>

    <el-row :gutter="16" class="stat-cards">
      <el-col :span="6"><el-card shadow="hover"><div class="stat-num">{{ stats.total }}</div><div class="stat-label">考核周期</div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><div class="stat-num">{{ stats.active }}</div><div class="stat-label">进行中</div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><div class="stat-num">{{ stats.completed }}</div><div class="stat-label">已完成</div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><div class="stat-num">{{ stats.employees }}</div><div class="stat-label">参与员工</div></el-card></el-col>
    </el-row>

    <el-table :data="cycles" border style="margin-top:20px" v-loading="loading">
      <el-table-column prop="name" label="考核名称" min-width="160"/>
      <el-table-column prop="year" label="年度" width="80" align="center"/>
      <el-table-column prop="period_type" label="周期类型" width="100" align="center">
        <template #default="{row}">{{ periodTypeMap[row.period_type]||row.period_type }}</template>
      </el-table-column>
      <el-table-column prop="start_date" label="开始日期" width="110"/>
      <el-table-column prop="end_date" label="结束日期" width="110"/>
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="{row}">
          <el-tag :type="statusType[row.status]" size="small">{{ statusMap[row.status] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="截止日期" width="320">
        <template #default="{row}">
          <span class="deadline-item">自评：{{ row.self_review_deadline }}</span>
          <span class="deadline-item">互评：{{ row.peer_review_deadline }}</span>
          <span class="deadline-item">上级：{{ row.manager_review_deadline }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{row}">
          <el-button link type="primary" @click="openReview(row)">评价</el-button>
          <el-button link type="primary" @click="openReport(row)">报告</el-button>
          <el-button link type="primary" @click="showDialog(row)">编辑</el-button>
          <el-dropdown @command="cmd=>handleCommand(cmd,row)">
            <el-button link type="primary">更多</el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="active" v-if="row.status==='draft'">启动</el-dropdown-item>
                <el-dropdown-item command="completed" v-if="row.status==='active'">完成</el-dropdown-item>
                <el-dropdown-item command="archived" v-if="row.status==='completed'">归档</el-dropdown-item>
                <el-dropdown-item command="generate">生成报告</el-dropdown-item>
                <el-dropdown-item command="delete" style="color:red">删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit?'编辑考核周期':'新建考核周期'" width="700px" :close-on-click-modal="false">
      <el-form :model="form" label-width="120px">
        <el-form-item label="考核名称"><el-input v-model="form.name" placeholder="如：2026年度上半年考核"/></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="年度"><el-input-number v-model="form.year" :min="2020" :max="2030"/></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="周期类型"><el-select v-model="form.period_type" style="width:100%">
            <el-option label="年度" value="annual"/><el-option label="半年" value="semi_annual"/>
            <el-option label="季度" value="quarterly"/><el-option label="月度" value="monthly"/>
          </el-select></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="开始日期"><el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width:100%"/></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="结束日期"><el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width:100%"/></el-form-item></el-col>
        </el-row>
        <el-divider>评价截止日期</el-divider>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="自评截止"><el-date-picker v-model="form.self_review_deadline" type="date" value-format="YYYY-MM-DD" style="width:100%"/></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="互评截止"><el-date-picker v-model="form.peer_review_deadline" type="date" value-format="YYYY-MM-DD" style="width:100%"/></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="上级评价截止"><el-date-picker v-model="form.manager_review_deadline" type="date" value-format="YYYY-MM-DD" style="width:100%"/></el-form-item></el-col>
        </el-row>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="2"/></el-form-item>
        <el-divider>考核维度</el-divider>
        <div v-for="(dim,idx) in form.dimensions" :key="idx" class="dimension-item">
          <el-row :gutter="8">
            <el-col :span="8"><el-input v-model="dim.name" placeholder="维度名称"/></el-col>
            <el-col :span="6"><el-select v-model="dim.dimension_type" style="width:100%">
              <el-option label="专业能力" value="skill"/><el-option label="通用能力" value="general"/>
              <el-option label="领导力" value="leadership"/><el-option label="价值观" value="value"/>
            </el-select></el-col>
            <el-col :span="4"><el-input-number v-model="dim.max_score" :min="1" :max="10" placeholder="最高分"/></el-col>
            <el-col :span="4"><el-input-number v-model="dim.weight" :min="0.1" :max="5" :step="0.1" placeholder="权重"/></el-col>
            <el-col :span="2"><el-button link type="danger" @click="form.dimensions.splice(idx,1)">删</el-button></el-col>
          </el-row>
        </div>
        <el-button link type="primary" @click="form.dimensions.push({name:'',dimension_type:'skill',weight:1,max_score:5})">+ 添加维度</el-button>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="saveCycle" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref,reactive,onMounted } from 'vue'
import { ElMessage,ElMessageBox } from 'element-plus'
import { getCycles,createCycle,updateCycle,updateCycleStatus,deleteCycle,generateReports } from '@/api/evaluation'
import { useRouter } from 'vue-router'

const router=useRouter()
const loading=ref(false),saving=ref(false),dialogVisible=ref(false),isEdit=ref(false)
const cycles=ref([])
const query=reactive({year:new Date().getFullYear(),status:''})
const form=reactive({id:null,name:'',year:new Date().getFullYear(),period_type:'semi_annual',start_date:'',end_date:'',self_review_deadline:'',peer_review_deadline:'',manager_review_deadline:'',remark:'',dimensions:[]})
const stats=reactive({total:0,active:0,completed:0,employees:490})
const years=Array.from({length:6},(_,i)=>new Date().getFullYear()-i)
const periodTypeMap={annual:'年度',semi_annual:'半年',quarterly:'季度',monthly:'月度'}
const statusMap={draft:'草稿',active:'进行中',completed:'已完成',archived:'已归档'}
const statusType={draft:'info',active:'warning',completed:'success',archived:''}

onMounted(()=>{ loadCycles() })

function loadCycles(){
  loading.value=true
  getCycles({year:query.year||undefined,status:query.status||undefined}).then(res=>{
    cycles.value=res||[]
    stats.total=cycles.value.length
    stats.active=cycles.value.filter(c=>c.status==='active').length
    stats.completed=cycles.value.filter(c=>c.status==='completed').length
    loading.value=false
  }).catch(()=>{loading.value=false})
}

function showDialog(row){
  if(row){
    Object.assign(form,{id:row.id,name:row.name,year:row.year,period_type:row.period_type,start_date:row.start_date,end_date:row.end_date,self_review_deadline:row.self_review_deadline,peer_review_deadline:row.peer_review_deadline,manager_review_deadline:row.manager_review_deadline,remark:row.remark||'',dimensions:[]})
    isEdit.value=true
  }else{
    Object.assign(form,{id:null,name:'',year:new Date().getFullYear(),period_type:'semi_annual',start_date:'',end_date:'',self_review_deadline:'',peer_review_deadline:'',manager_review_deadline:'',remark:'',dimensions:[{name:'专业能力',dimension_type:'skill',weight:1,max_score:5},{name:'团队协作',dimension_type:'general',weight:1,max_score:5},{name:'工作态度',dimension_type:'general',weight:1,max_score:5}]})
    isEdit.value=false
  }
  dialogVisible.value=true
}

function saveCycle(){
  if(!form.name||!form.start_date||!form.end_date){ElMessage.warning('请填写完整信息');return}
  const data={...form,dimensions:form.dimensions.filter(d=>d.name)}
  const api=isEdit.value?updateCycle(form.id,data):createCycle(data)
  saving.value=true
  api.then(()=>{ElMessage.success('保存成功');dialogVisible.value=false;loadCycles()}).catch(e=>ElMessage.error('保存失败')).finally(()=>{saving.value=false})
}

function handleCommand(cmd,row){
  if(cmd==='delete'){
    ElMessageBox.confirm('确定删除该考核周期？','提示',{type:'warning'}).then(()=>deleteCycle(row.id).then(()=>{ElMessage.success('删除成功');loadCycles()}).catch(()=>ElMessage.error('删除失败'))).catch(()=>{})
  }else if(cmd==='generate'){
    generateReports(row.id).then(()=>{ElMessage.success('报告生成成功');router.push('/evaluation/report/'+row.id)}).catch(()=>ElMessage.error('生成失败'))
  }else{
    updateCycleStatus(row.id,cmd).then(()=>{ElMessage.success('状态已更新');loadCycles()}).catch(()=>ElMessage.error('更新失败'))
  }
}

function openReview(row){router.push('/evaluation/review/'+row.id)}
function openReport(row){router.push('/evaluation/report/'+row.id)}
</script>

<style scoped>
.evaluation-container{padding:20px}
.page-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.page-header h2{margin:0;font-size:18px;color:#333}
.filter-bar{display:flex;gap:12px;margin-bottom:16px}
.stat-cards .stat-num{font-size:28px;font-weight:bold;color:#ec6921;text-align:center}
.stat-cards .stat-label{text-align:center;color:#999;font-size:13px;margin-top:4px}
.deadline-item{display:inline-block;margin-right:12px;font-size:12px;color:#666}
.dimension-item{margin-bottom:12px;padding:12px;background:#f5f7fa;border-radius:4px}
</style>
