import sys
sys.path.insert(0, r'C:\Users\Administrator\.qclaw\workspace-agent-8fd3bdac\attendance_system\backend')

from app.core.database import SessionLocal, engine
from app.models.setting import SystemSetting, OperationLog

# Create tables
SystemSetting.__table__.create(engine, checkfirst=True)
OperationLog.__table__.create(engine, checkfirst=True)

db = SessionLocal()

settings = [
    ("company_name", "海昌新材", "公司名称"),
    ("company_short_name", "海昌新材", "公司简称"),
    ("company_credit_code", "", "统一社会信用代码"),
    ("company_address", "", "公司地址"),
    ("company_phone", "", "联系电话"),
    ("attendance_work_start_time", "08:30", "上班时间"),
    ("attendance_work_end_time", "17:30", "下班时间"),
    ("attendance_late_tolerance", "5", "迟到容忍"),
    ("attendance_early_tolerance", "5", "早退容忍"),
    ("attendance_work_days", '["1","2","3","4","5"]', "工作日"),
    ("leave_annual_days", "5", "年假天数"),
    ("leave_sick_days", "10", "病假天数"),
    ("leave_personal_days", "5", "事假天数"),
    ("leave_compensatory_days", "0", "调休天数"),
    ("system_name", "海昌新材人事考勤系统", "系统名称"),
    ("system_session_timeout", "120", "登录有效期"),
    ("system_auto_backup", "true", "自动备份"),
    ("system_backup_interval", "daily", "备份周期"),
    ("system_theme", "light", "系统主题"),
]

for key, value, desc in settings:
    s = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not s:
        s = SystemSetting(key=key, value=value, description=desc)
        db.add(s)
    else:
        s.value = value

db.commit()
print("Settings seeded successfully")
