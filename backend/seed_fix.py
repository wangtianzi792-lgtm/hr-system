# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datetime import date, datetime, timedelta, time
import random

# Force UTF-8 for stdout
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine('sqlite:///./attendance.db', connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# Import models after Base
from app.models.employee import Employee
from app.models.department import Department
from app.models.attendance import AttendanceRecord
from app.models.scheduling import Shift
from app.models.device import Device

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Clear all
db.query(AttendanceRecord).delete()
db.query(Employee).delete()
db.query(Department).delete()
db.query(Shift).delete()
db.query(Device).delete()
db.commit()

# Device
dev = Device(name="xFace100-主机", ip_address="192.168.1.201", port=4370, device_type="xFace100", serial_number="SN20250101", status="online", location="一楼大门", is_active=True)
db.add(dev)
db.flush()

# Departments
dept_data = [("行政部", "ADMIN", 1), ("技术部", "TECH", 2), ("销售部", "SALES", 3), ("生产部", "PROD", 4)]
deps = []
for name, code, order in dept_data:
    d = Department(name=name, code=code, sort_order=order)
    db.add(d)
    deps.append(d)
db.flush()

# Employees
emp_data = [
    ("E001", "张伟", "男", "13812340001", deps[1].id, "Java开发工程师", date(2025,10,25), "60001001", 1),
    ("E002", "李娜", "女", "13812340002", deps[1].id, "前端开发工程师", date(2026,1,23), "60001002", 2),
    ("E003", "王强", "男", "13812340003", deps[2].id, "销售经理", date(2025,4,23), "60001003", 3),
    ("E004", "陈静", "女", "13812340004", deps[0].id, "行政主管", date(2025,3,19), "60001004", 4),
    ("E005", "刘洋", "男", "13812340005", deps[3].id, "生产主管", date(2025,10,5), "60001005", 5),
    ("E006", "赵文", "男", "13812340006", deps[1].id, "测试工程师", date(2026,3,1), "60001006", 6),
    ("E007", "周梅", "女", "13812340007", deps[2].id, "销售代表", date(2026,2,10), "60001007", 7),
    ("E008", "吴海", "男", "13812340008", deps[3].id, "质检员", date(2025,8,15), "60001008", 8),
]
emp_objs = []
for ed in emp_data:
    e = Employee(employee_no=ed[0], name=ed[1], gender=ed[2], phone=ed[3], department_id=ed[4], position=ed[5], entry_date=ed[6], card_no=ed[7], zk_user_id=ed[8], status="active", is_active=True, zk_password="123456")
    db.add(e)
    emp_objs.append(e)
db.flush()

# Shifts
shifts_data = [
    ("早班", "day", time(8,0), time(9,5), time(17,0), time(18,0), "8", "#409EFF"),
    ("中班", "middle", time(9,0), time(10,0), time(18,0), time(19,0), "8", "#67C23A"),
    ("夜班", "night", time(20,0), time(21,0), time(4,0), time(5,30), "8", "#E6A23C"),
]
for sd in shifts_data:
    s = Shift(name=sd[0], shift_type=sd[1], check_in_start=sd[2], check_in_end=sd[3], check_out_start=sd[4], check_out_end=sd[5], work_hours=sd[6], color=sd[7], is_active=True)
    db.add(s)
db.flush()

# Attendance records
today = date.today()
total_rec = 0
for i in range(6, -1, -1):
    d = today - timedelta(days=i)
    if d.weekday() >= 5:
        continue
    for emp in emp_objs:
        h_in = 8 if random.random() > 0.15 else 9
        m_in = random.randint(0, 45)
        status_in = "late" if (h_in >= 9 and m_in > 5) else "normal"
        db.add(AttendanceRecord(employee_id=emp.id, device_id=1, punch_date=d, punch_time=datetime(d.year,d.month,d.day,h_in,m_in,random.randint(0,59)), punch_type="check_in", verify_type="face", status=status_in))
        total_rec += 1
        h_out = random.choice([17,17,18,18,18,19])
        m_out = random.randint(0, 59)
        status_out = "early" if h_out < 17 else "normal"
        db.add(AttendanceRecord(employee_id=emp.id, device_id=1, punch_date=d, punch_time=datetime(d.year,d.month,d.day,h_out,m_out,random.randint(0,59)), punch_type="check_out", verify_type="face", status=status_out))
        total_rec += 1

db.commit()

# Verify
print("Done. Verifying...")
for d in db.query(Department).all():
    print(f"Dept: {d.id} = {d.name}")
for e in db.query(Employee).all():
    print(f"Emp: {e.employee_no} = {e.name}")
db.close()
