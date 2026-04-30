import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/layout/index.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '工作台', icon: 'HomeFilled' }
      },
      {
        path: 'attendance',
        name: 'Attendance',
        component: () => import('@/views/attendance/index.vue'),
        meta: { title: '打卡记录', icon: 'Calendar' }
      },
      {
        path: 'attendance/rules',
        name: 'AttendanceRules',
        component: () => import('@/views/attendance/rules.vue'),
        meta: { title: '考勤规则', icon: 'Setting' }
      },
      {
        path: 'attendance/calendar',
        name: 'AttendanceCalendar',
        component: () => import('@/views/attendance/calendar.vue'),
        meta: { title: '考勤日历', icon: 'Calendar' }
      },
      {
        path: 'work-hours/shifts',
        name: 'WorkHoursShifts',
        component: () => import('@/views/work-hours/shifts.vue'),
        meta: { title: '班次配置', icon: 'Clock' }
      },
      {
        path: 'work-hours/employee-shifts',
        name: 'WorkHoursEmployeeShifts',
        component: () => import('@/views/work-hours/employee-shifts.vue'),
        meta: { title: '员工排班', icon: 'User' }
      },
      {
        path: 'work-hours/report',
        name: 'WorkHoursReport',
        component: () => import('@/views/work-hours/report.vue'),
        meta: { title: '工时报表', icon: 'DataLine' }
      },
      {
        path: 'shift-adjustments',
        name: 'ShiftAdjustments',
        component: () => import('@/views/work-hours/adjustments.vue'),
        meta: { title: '调休管理', icon: 'Swap' }
      },
      
      {
        path: 'leave',
        name: 'Leave',
        component: () => import('@/views/leave/index.vue'),
        meta: { title: '请假申请', icon: 'Document' }
      },
      {
        path: 'overtime',
        name: 'Overtime',
        component: () => import('@/views/overtime/index.vue'),
        meta: { title: '加班申请', icon: 'Timer' }
      },
      {
        path: 'approval',
        name: 'Approval',
        component: () => import('@/views/approval/index.vue'),
        meta: { title: '审批中心', icon: 'Checked' }
      },
      {
        path: 'employees',
        name: 'Employees',
        component: () => import('@/views/employees/index.vue'),
        meta: { title: '员工管理', icon: 'UserFilled' }
      },
      {
        path: 'departments',
        name: 'Departments',
        component: () => import('@/views/departments/index.vue'),
        meta: { title: '部门管理', icon: 'OfficeBuilding' }
      },
      {
        path: 'work-hours',
        name: 'WorkHours',
        component: () => import('@/views/work-hours/index.vue'),
        meta: { title: '工时配置', icon: 'Timer' }
      },
      {
        path: 'roster',
        name: 'Roster',
        component: () => import('@/views/roster/index.vue'),
        meta: { title: '花名册（在职）', icon: 'Document' }
      },
      {
        path: 'onboarding',
        name: 'Onboarding',
        component: () => import('@/views/onboarding/index.vue'),
        meta: { title: '入职管理', icon: 'Plus' }
      },
      {
        path: 'offboarding',
        name: 'Offboarding',
        component: () => import('@/views/offboarding/index.vue'),
        meta: { title: '离职管理', icon: 'Minus' }
      },
      {
        path: 'devices',
        name: 'Devices',
        component: () => import('@/views/devices/index.vue'),
        meta: { title: '考勤设备', icon: 'Monitor' }
      },
      {
        path: 'reports/daily',
        name: 'ReportsDaily',
        component: () => import('@/views/reports/daily.vue'),
        meta: { title: '日报', icon: 'Document' }
      },
      {
        path: 'reports/monthly',
        name: 'ReportsMonthly',
        component: () => import('@/views/reports/monthly.vue'),
        meta: { title: '月报', icon: 'DocumentChecked' }
      },
      {
        path: 'reports/statistics',
        name: 'ReportsStatistics',
        component: () => import('@/views/reports/statistics.vue'),
        meta: { title: '统计分析', icon: 'TrendCharts' }
      },
      {
        path: 'evaluation',
        name: 'Evaluation',
        component: () => import('@/views/evaluation/index.vue'),
        meta: { title: '360考核', icon: 'DataAnalysis' }
      },
      {
        path: 'evaluation/review/:id/:type',
        name: 'EvaluationReview',
        component: () => import('@/views/evaluation/review.vue'),
        meta: { title: '考核评价', icon: 'Edit' }
      },
      {
        path: 'evaluation/report/:id',
        name: 'EvaluationReport',
        component: () => import('@/views/evaluation/report.vue'),
        meta: { title: '考核报告', icon: 'DataLine' }
      },
      {
        path: 'roles',
        name: 'Roles',
        component: () => import('@/views/roles/index.vue'),
        meta: { title: '角色管理', icon: 'Key' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/index.vue'),
        meta: { title: '系统设置', icon: 'Setting' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/index.vue'),
        meta: { title: '个人中心', icon: 'User' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (!to.meta.public && !userStore.token) {
    next('/login')
  } else {
    next()
  }
})

export default router
