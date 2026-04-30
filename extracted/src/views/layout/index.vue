<template>
  <el-container class="layout-container">
    <!-- 左侧侧边栏 - 简道云风格深色 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <!-- Logo区域 -->
      <div class="logo-area">
        <div class="logo-icon">HR</div>
        <span class="logo-text" v-if="!isCollapse">海昌新材</span>
      </div>
      
      <!-- 菜单 -->
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="false"
        router
        class="sidebar-menu"
        background-color="#001529"
        text-color="#a6adb4"
        active-text-color="#fff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>
        
        <el-sub-menu index="/attendance">
          <template #title>
            <el-icon><Calendar /></el-icon>
            <span>考勤管理</span>
          </template>
          <el-menu-item index="/attendance">打卡记录</el-menu-item>
          <el-menu-item index="/attendance/rules">考勤规则</el-menu-item>
          <el-menu-item index="/attendance/calendar">考勤日历</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="/work-hours">
          <template #title>
            <el-icon><Clock /></el-icon>
            <span>工时配置</span>
          </template>
          <el-menu-item index="/work-hours/shifts">班次配置</el-menu-item>
          <el-menu-item index="/work-hours/employee-shifts">员工排班</el-menu-item>
          <el-menu-item index="/work-hours/report">工时报表</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="/attendance-manage">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>人事审批</span>
          </template>
          <el-menu-item index="/leave">请假申请</el-menu-item>
          <el-menu-item index="/overtime">加班申请</el-menu-item>
          <el-menu-item index="/shift-adjustments">调休管理</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/employees">
          <el-icon><UserFilled /></el-icon>
          <template #title>员工管理</template>
        </el-menu-item>

        <el-sub-menu index="/roster">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>人员变动</span>
          </template>
          <el-menu-item index="/roster">花名册（在职）</el-menu-item>
          <el-menu-item index="/onboarding">入职管理</el-menu-item>
          <el-menu-item index="/offboarding">离职管理</el-menu-item>
        </el-sub-menu>
        
        <el-menu-item index="/departments">
          <el-icon><OfficeBuilding /></el-icon>
          <template #title>部门管理</template>
        </el-menu-item>
        
        <el-menu-item index="/devices">
          <el-icon><Monitor /></el-icon>
          <template #title>考勤设备</template>
        </el-menu-item>
        
        <el-menu-item index="/evaluation">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>360考核</template>
        </el-menu-item>
        
        <el-sub-menu index="/reports">
          <template #title>
            <el-icon><TrendCharts /></el-icon>
            <span>报表统计</span>
          </template>
          <el-menu-item index="/reports/daily">日报</el-menu-item>
          <el-menu-item index="/reports/monthly">月报</el-menu-item>
          <el-menu-item index="/reports/statistics">统计分析</el-menu-item>
        </el-sub-menu>
        
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>

        <el-menu-item index="/roles">
          <el-icon><Key /></el-icon>
          <template #title>角色管理</template>
        </el-menu-item>
      </el-menu>
      
      <!-- 折叠按钮 -->
      <div class="collapse-btn" @click="toggleCollapse">
        <el-icon><Fold v-if="!isCollapse"/><Expand v-else/></el-icon>
      </div>
    </el-aside>

    <!-- 右侧主内容区 -->
    <el-container class="main-container">
      <!-- 顶部Header -->
      <el-header class="top-header">
        <div class="breadcrumb">
          <el-icon class="home-icon"><HomeFilled /></el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index">
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-actions">
          <el-tooltip content="消息通知" placement="bottom">
            <el-badge :value="3" class="action-item">
              <el-icon><Bell /></el-icon>
            </el-badge>
          </el-tooltip>
          
          <el-tooltip content="全屏" placement="bottom">
            <el-icon class="action-item" @click="toggleFullscreen">
              <FullScreen />
            </el-icon>
          </el-tooltip>
          
          <el-dropdown @command="handleCommand" class="user-dropdown">
            <div class="user-info">
              <el-avatar :size="32" :src="userAvatar" class="user-avatar">
                {{ userStore.userInfo?.username?.charAt(0)?.toUpperCase() || 'A' }}
              </el-avatar>
              <span class="username">{{ userStore.userInfo?.username || '管理员' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>账号设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="content-main">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isCollapse = ref(false)
const userAvatar = ref('')

const activeMenu = computed(() => route.path)

const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  return matched.map(item => ({
    title: item.meta.title,
    path: item.path
  }))
})

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确认退出登录？', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      userStore.logout()
      router.push('/login')
      ElMessage.success('已退出登录')
    })
  } else if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'settings') {
    router.push('/settings')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏 - 简道云风格深色 */
.sidebar {
  background-color: #001529;
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
  position: relative;
}

.logo-area {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 0 16px;
  background: linear-gradient(135deg, #002140 0%, #001529 100%);
  border-bottom: 1px solid rgba(255,255,255,0.1);
  flex-shrink: 0;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #ec6921 0%, #f0884a 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: bold;
  font-size: 14px;
  flex-shrink: 0;
}

.logo-text {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
  letter-spacing: 0.5px;
}

/* 菜单样式 */
.sidebar-menu {
  flex: 1;
  border-right: none;
  padding: 8px 0;
  overflow-y: auto;
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  height: 44px;
  line-height: 44px;
  margin: 2px 8px;
  border-radius: 4px;
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background-color: rgba(236, 105, 33, 0.15) !important;
  color: #fff !important;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #ec6921 !important;
  color: #fff !important;
}

.sidebar-menu :deep(.el-sub-menu.is-active .el-sub-menu__title) {
  color: #ec6921 !important;
}

.sidebar-menu :deep(.el-icon) {
  font-size: 18px;
  margin-right: 12px;
}

/* 折叠按钮 */
.collapse-btn {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #a6adb4;
  cursor: pointer;
  border-top: 1px solid rgba(255,255,255,0.1);
  transition: all 0.3s;
  flex-shrink: 0;
}

.collapse-btn:hover {
  color: #fff;
  background-color: rgba(236, 105, 33, 0.2);
}

/* 主内容区 */
.main-container {
  background-color: #f0f2f5;
  flex-direction: column;
  min-width: 0;
}

/* 顶部Header */
.top-header {
  height: 64px;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 100;
  flex-shrink: 0;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 12px;
}

.home-icon {
  color: #ec6921;
  font-size: 18px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.action-item {
  font-size: 20px;
  color: #666;
  cursor: pointer;
  transition: color 0.3s;
}

.action-item:hover {
  color: #ec6921;
}

.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f5f5;
}

.user-avatar {
  background: linear-gradient(135deg, #ec6921 0%, #f0884a 100%);
  color: #fff;
  font-weight: 600;
}

.username {
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

/* 内容区 */
.content-main {
  padding: 20px;
  overflow-y: auto;
  background-color: #f0f2f5;
}

/* 页面切换动画 */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
