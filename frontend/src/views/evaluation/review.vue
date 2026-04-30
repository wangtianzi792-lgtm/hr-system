<template>
  <div class="review-container">
    <div class="page-header">
      <el-button @click="goBack">返回</el-button>
      <h2>{{ cycleName }} - {{ reviewTypeLabel }}评价</h2>
    </div>

    <el-card v-if="!selectedReviewee" style="margin-bottom:20px">
      <el-form inline>
        <el-form-item label="选择被评价人">
          <el-select v-model="searchDept" placeholder="部门" clearable style="width:150px" @change="loadEmployees">
            <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id"/>
          </el-select>
          <el-select v-model="selectedEmpId" placeholder="员工" filterable style="width:200px;margin-left:8px">
            <el-option v-for="e in employees" :key="e.id" :label="e.employee_id+' - '+e.name" :value="e.id"/>
          </el-select>
          <el-button type="primary" style="margin-left:8px" @click="selectReviewee" :disabled="!selectedEmpId">开始评价</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="selectedReviewee">
      <template #header>
        <div class="card-header">
          <span>被评价人：<b>{{ selectedReviewee.name }}</b> ({{ selectedReviewee.employee_id }})</span>
          <el-button link type="primary" @click="selectedReviewee=null;scores={};comments={}">重新选择</el-button>
        </div>
      </template>

      <el-form v-if="reviewType==='self'" label-width="100px" style="margin-bottom:20px">
        <el-form-item label="自我评价">
          <el-input v-model="selfReviewText" type="textarea" :rows="5" placeholder="请从工作业绩、能力提升、团队协作、未来规划等方面进行自我评价..."/>
        </el-form-item>
      </el-form>

      <div class="dimension-list">
        <div v-for="dim in dimensions" :key="dim.id" class="dimension-card">
          <div class="dim-header">
            <span class="dim-name">{{ dim.name }}</span>
            <el-tag size="small">{{ dimTypeMap[dim.dimension_type]||dim.dimension_type }}</el-tag>
            <span class="dim-weight">权重: {{ dim.weight }}</span>
          </div>
          <div class="dim-score">
            <span>评分：</span>
            <el-rate v-model="scores[dim.id]" :max="dim.max_score" show-score/>
            <span class="score-text">{{ scores[dim.id]||0 }} / {{ dim.max_score }} 分</span>
          </div>
          <div class="dim-comment">
            <el-input v-model="comments[dim.id]" type="textarea" :rows="2" :placeholder="'请对'+dim.name+'进行简要评价...'" />
          </div>
        </div>
      </div>

      <div class="submit-area">
        <el-button @click="goBack">取消</el-button>
        <el-button type="primary" @click="submitReview" :loading="submitting">提交评价</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref,computed,onMounted } from 'vue'
import { useRoute,useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getCycleDetail,submitEvaluation } from '@/api/evaluation'
import { getEmployees } from '@/api/employees'
import { getDepartments } from '@/api/departments'

const route=useRoute(),router=useRouter()
const cycleId=Number(route.params.id)
const reviewType=route.params.type||'self'
const cycleName=ref(''),dimensions=ref([])
const departments=ref([]),employees=ref([])
const selectedEmpId=ref(null),selectedReviewee=ref(null)
const selfReviewText=ref('')
const scores=ref({}),comments=ref({})
const submitting=ref(false)
const searchDept=ref(null)

const reviewTypeLabel=computed(()=>({self:'自评',peer:'互评',manager:'上级评价'})[reviewType]||reviewType)
const dimTypeMap={skill:'专业能力',general:'通用能力',leadership:'领导力',value:'价值观'}

onMounted(()=>{
  loadCycleDetail()
  loadDepartments()
  loadEmployees()
})

function loadCycleDetail(){
  getCycleDetail(cycleId).then(res=>{
    cycleName.value=res.name
    dimensions.value=res.dimensions||[]
  }).catch(()=>ElMessage.error('加载考核详情失败'))
}

function loadDepartments(){
  getDepartments().then(res=>{departments.value=res||[]}).catch(()=>{})
}

function loadEmployees(){
  getEmployees({department_id:searchDept.value||undefined,status:'active'}).then(res=>{
    employees.value=res||[]
  }).catch(()=>{})
}

function selectReviewee(){
  const emp=employees.value.find(e=>e.id===selectedEmpId.value)
  if(emp) selectedReviewee.value=emp
}

async function submitReview(){
  const dimList=Object.keys(scores.value)
  if(dimList.length===0){ElMessage.warning('请至少评一个维度');return}
  const scoreList=dimList.map(did=>({dimension_id:Number(did),score:Number(scores.value[did])||0,comment:comments.value[did]||null}))
  const data={
    cycle_id:cycleId,
    reviewee_id:selectedReviewee.value.id,
    reviewer_id:1,
    review_type:reviewType,
    scores:scoreList,
    self_review_text:reviewType==='self'?selfReviewText.value:null
  }
  submitting.value=true
  try{
    await submitEvaluation(data)
    ElMessage.success('评价提交成功')
    router.push('/evaluation')
  }catch(e){
    ElMessage.error(e.response?.data?.detail||'提交失败')
  }finally{
    submitting.value=false
  }
}

function goBack(){router.push('/evaluation')}
</script>

<style scoped>
.review-container{padding:20px}
.page-header{display:flex;align-items:center;gap:16px;margin-bottom:20px}
.page-header h2{margin:0;font-size:18px}
.card-header{display:flex;justify-content:space-between;align-items:center}
.dimension-list{margin:20px 0}
.dimension-card{margin-bottom:16px;padding:16px;border:1px solid #e4e7ed;border-radius:8px}
.dim-header{display:flex;align-items:center;gap:10px;margin-bottom:12px}
.dim-name{font-weight:bold;font-size:15px}
.dim-weight{color:#999;font-size:13px}
.dim-score{display:flex;align-items:center;gap:12px;margin:12px 0}
.score-text{font-weight:bold;color:#ec6921}
.submit-area{text-align:center;margin-top:24px;padding-top:20px;border-top:1px solid #eee}
</style>
