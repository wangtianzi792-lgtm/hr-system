<template>
  <div class=login-container>
    <div class=login-left>
      <div class=brand-area>
        <img src=/logo.png alt=海昌新材 class=login-logo />
        <h1 class=brand-title>海昌新材</h1>
        <p class=brand-subtitle>人事考勤管理系统</p>
      </div>
    </div>
    
    <el-card class=login-card shadow=always>
      <template #header>
        <h2 class=login-title>用户登录</h2>
      </template>
      
      <el-form
        ref=loginFormRef
        :model=loginForm
        :rules=loginRules
        label-position=top
      >
        <el-form-item label=用户名 prop=username>
          <el-input
            v-model=loginForm.username
            placeholder=请输入用户名
            prefix-icon=User
          />
        </el-form-item>
        
        <el-form-item label=密码 prop=password>
          <el-input
            v-model=loginForm.password
            type=password
            placeholder=请输入密码
            prefix-icon=Lock
            show-password
            @keyup.enter=handleLogin
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type=primary
            :loading=loading
            class=login-button
            @click=handleLogin
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { login } from '@/api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  const valid = await loginFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await login({
      username: loginForm.username,
      password: loginForm.password
    })
    
    // 存储token和用户信息
    userStore.setToken(res.access_token)
    userStore.setUserInfo({
      id: res.user_id,
      username: res.username,
      nickname: res.nickname,
      role: res.role
    })
    
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    // 错误已在拦截器中处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  background: linear-gradient(135deg, #ec6921 0%, #d45416 50%, #b84310 100%);
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -20%;
  width: 80%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
  pointer-events: none;
}

.login-container::after {
  content: '';
  position: absolute;
  bottom: -30%;
  right: -10%;
  width: 60%;
  height: 150%;
  background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 60%);
  pointer-events: none;
}

.login-left {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.brand-area {
  text-align: center;
  color: #fff;
}

.login-logo {
  width: 180px;
  margin-bottom: 24px;
  filter: brightness(0) invert(1);
  opacity: 0.95;
}

.brand-title {
  font-size: 36px;
  font-weight: bold;
  margin: 0 0 12px 0;
  text-shadow: 0 2px 8px rgba(0,0,0,0.15);
  letter-spacing: 4px;
}

.brand-subtitle {
  font-size: 18px;
  opacity: 0.9;
  margin: 0;
  letter-spacing: 6px;
  font-weight: 300;
}

.login-card {
  width: 420px;
  margin: 40px;
  border-radius: 12px;
  z-index: 1;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.login-title {
  text-align: center;
  color: #ec6921;
  margin: 0;
  font-size: 22px;
  font-weight: bold;
}

.login-button {
  width: 100%;
  background-color: #ec6921 !important;
  border-color: #ec6921 !important;
  font-size: 16px;
  letter-spacing: 4px;
  padding: 12px 0;
}

.login-button:hover {
  background-color: #d45416 !important;
  border-color: #d45416 !important;
}
</style>
