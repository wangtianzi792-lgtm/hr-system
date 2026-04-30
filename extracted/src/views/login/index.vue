<template>
  <div class="login-container">
    <!-- 视频背景 -->
    <video class="login-video" :src="'/banner.mp4'" autoplay muted loop playsinline></video>
    
    <!-- 右侧内容区 -->
    <div class="login-right">
      <!-- 登录卡片 -->
      <el-card class="login-card">
        <!-- 顶部品牌区 -->
        <div class="card-header">
          <img src="/logo.png" alt="海昌新材" class="card-logo" />
          <div class="card-brand-text">
            <h1 class="card-title">海昌新材</h1>
            <p class="card-subtitle">人事考勤管理系统</p>
          </div>
        </div>
        
        <el-divider class="card-divider" />
        
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          label-position="top"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              prefix-icon="User"
              size="large"
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
              size="large"
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              :loading="loading"
              class="login-button"
              size="large"
              @click="handleLogin"
            >
              登 录
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
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
  width: 100vw;
  position: relative;
  overflow: hidden;
  background: #000;
}

.login-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}

.login-right {
  position: relative;
  z-index: 1;
  height: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 12vh;
  box-sizing: border-box;
}

.login-card {
  width: 400px;
  border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.4);
  background: rgba(255, 255, 255, 0.72) !important;
  border: 1px solid rgba(236, 105, 33, 0.2);
  box-shadow: 0 8px 32px rgba(236,105,33,0.08), 0 0 80px rgba(236,105,33,0.04) inset;
}

.card-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 24px 12px;
}

.card-logo {
  width: 154px;
  height: 25px;
  object-fit: contain;
  margin-bottom: 12px;
}

.card-brand-text {
  width: 100%;
  text-align: center;
}

.card-title {
  font-size: 26px;
  font-weight: bold;
  color: #ec6921;
  letter-spacing: 3px;
  margin: 0 0 4px 0;
  white-space: nowrap;
}

.card-subtitle {
  font-size: 13px;
  color: #999;
  letter-spacing: 4px;
  margin: 0;
  white-space: nowrap;
}

.card-divider {
  margin: 0 24px 24px;
}

.login-button {
  width: 100%;
  background: linear-gradient(135deg, #ec6921 0%, #d45416 100%) !important;
  border: none !important;
  font-size: 18px;
  letter-spacing: 8px;
  padding: 14px 0;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(236, 105, 33, 0.4);
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #333;
}

@media (max-width: 768px) {
  .login-right {
    padding: 40px 30px;
    align-items: center;
    justify-content: center;
  }
  .login-card {
    width: 100%;
  }
}
</style>