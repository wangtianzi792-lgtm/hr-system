// 导出工具函数

/**
 * 将数据导出为Excel文件
 * @param {Array} data - 表格数据
 * @param {Array} columns - 列配置 [{ prop, label, width }]
 * @param {String} filename - 文件名
 */
export function exportToExcel(data, columns, filename) {
  // 构建CSV内容
  const BOM = '\uFEFF' // UTF-8 BOM
  
  // 表头
  const headers = columns.map(col => col.label).join(',')
  
  // 数据行
  const rows = data.map(row => {
    return columns.map(col => {
      const value = row[col.prop]
      // 处理包含逗号或换行的值，用引号包裹
      if (value !== null && value !== undefined) {
        const str = String(value)
        if (str.includes(',') || str.includes('\n') || str.includes('"')) {
          return `"${str.replace(/"/g, '""')}"`
        }
        return str
      }
      return ''
    }).join(',')
  })
  
  const csvContent = BOM + headers + '\n' + rows.join('\n')
  
  // 创建下载链接
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  
  link.setAttribute('href', url)
  link.setAttribute('download', `${filename}_${formatDate(new Date())}.csv`)
  link.style.visibility = 'hidden'
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  URL.revokeObjectURL(url)
}

/**
 * 格式化日期
 * @param {Date} date 
 * @returns {String} YYYY-MM-DD
 */
function formatDate(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}${month}${day}`
}

/**
 * 导出日报数据
 */
export function exportDailyReport(data, dateRange) {
  const columns = [
    { prop: 'employee_no', label: '工号' },
    { prop: 'name', label: '姓名' },
    { prop: 'department', label: '部门' },
    { prop: 'should_attend', label: '应出勤' },
    { prop: 'actual_attend', label: '实出勤' },
    { prop: 'normal', label: '正常' },
    { prop: 'late', label: '迟到' },
    { prop: 'early', label: '早退' },
    { prop: 'absent', label: '缺勤' },
    { prop: 'work_hours', label: '工时' },
    { prop: 'attendance_rate', label: '出勤率' }
  ]
  
  const startDate = dateRange && dateRange[0] ? dateRange[0] : ''
  const endDate = dateRange && dateRange[1] ? dateRange[1] : ''
  const filename = `考勤日报_${startDate}_${endDate}`
  
  exportToExcel(data, columns, filename)
}

/**
 * 导出月报数据
 */
export function exportMonthlyReport(data, month) {
  const columns = [
    { prop: 'employee_no', label: '工号' },
    { prop: 'name', label: '姓名' },
    { prop: 'department', label: '部门' },
    { prop: 'should_attend', label: '应出勤' },
    { prop: 'actual_attend', label: '实出勤' },
    { prop: 'normal', label: '正常' },
    { prop: 'late', label: '迟到' },
    { prop: 'early', label: '早退' },
    { prop: 'absent', label: '缺勤' },
    { prop: 'leave_days', label: '请假天数' },
    { prop: 'overtime_hours', label: '加班工时' },
    { prop: 'work_hours', label: '工时' },
    { prop: 'attendance_rate', label: '出勤率' }
  ]
  
  const filename = `考勤月报_${month}`
  exportToExcel(data, columns, filename)
}

/**
 * 导出员工列表
 */
export function exportEmployees(data) {
  const columns = [
    { prop: 'employee_no', label: '工号' },
    { prop: 'name', label: '姓名' },
    { prop: 'department_name', label: '部门' },
    { prop: 'position', label: '职位' },
    { prop: 'phone', label: '手机号' },
    { prop: 'email', label: '邮箱' },
    { prop: 'status', label: '状态' },
    { prop: 'hire_date', label: '入职日期' }
  ]
  
  exportToExcel(data, columns, '员工列表')
}

/**
 * 导出考勤记录
 */
export function exportAttendanceRecords(data) {
  const columns = [
    { prop: 'employee_name', label: '姓名' },
    { prop: 'department_name', label: '部门' },
    { prop: 'date', label: '日期' },
    { prop: 'check_in', label: '上班打卡' },
    { prop: 'check_out', label: '下班打卡' },
    { prop: 'status', label: '状态' },
    { prop: 'work_hours', label: '工时' },
    { prop: 'device_name', label: '打卡设备' }
  ]
  
  exportToExcel(data, columns, '考勤记录')
}
