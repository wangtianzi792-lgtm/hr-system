# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datetime import date, datetime, timedelta, time
import random

from app.core.database import SessionLocal, engine, Base
from app.models.employee import Employee
from app.models.department import Department
from app.models.attendance import AttendanceRecord
from app.models.scheduling import Shift
from app.models.device import Device

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Delete in order to respect FK
db.query(AttendanceRecord).delete()
db.query(Employee).delete()
db.query(Department).delete()
db.query(Shift).delete()
db.query(Device).delete()
db.commit()

# Add device first
dev = Device(name="xFace100-主机", ip_address="192.168.1.201", port=4370, device_type="xFace100", serial_number="SN20250101", status="online", location="一楼大门", is_active=True)
db.add(dev)
db.flush()

depts = [
    Department(name="行政部", code="ADMIN", sort_order=1),
    Department(name="技术部", code="TECH", sort_order=2),
    Department(name="销售部", code="SALES", sort_order=3),
    Department(name="生产部", code="PROD", sort_order=4),
]
db.add_all(depts)
db.flush()

emps = [
    {"employee_no": "E001", "name": "张伟", "gender": "男", "phone": "13812340001", "department_id": 2, "position": "Java开发工程师", "entry_date": date(2025,10,25), "card_no": "60001001", "zk_user_id": 1},
    {"employee_no": "E002", "name": "李娜", "gender": "女", "phone": "13812340002", "department_id": 2, "position": "前端开发工程师", "entry_date": date(2026,1,23), "card_no": "60001002", "zk_user_id": 2},
    {"employee_no": "E003", "name": "王强", "gender": "男", "phone": "13812340003", "department_id": 3, "position": "销售经理", "entry_date": date(2025,4,23), "card_no": "60001003", "zk_user_id": 3},
    {"employee_no": "E004", "name": "陈静", "gender": "女", "phone": "13812340004", "department_id": 1, "position": "行政主管", "entry_date": date(2025,3,19), "card_no": "60001004", "zk_user_id": 4},
    {"employee_no": "E005", "name": "刘洋", "gender": "男", "phone": "13812340005", "department_id": 4, "position": "生产主管", "entry_date": date(2025,10,5), "card_no": "60001005", "zk_user_id": 5},
    {"employee_no": "E006", "name": "赵文", "gender": "男", "phone": "13812340006", "department_id": 2, "position": "测试工程师", "entry_date": date(2026,3,1), "card_no": "60001006", "zk_user_id": 6},
    {"employee_no": "E007", "name": "周梅", "gender": "女", "phone": "13812340007", "department_id": 3, "position": "销售代表", "entry_date": date(2026,2,10), "card_no": "60001007", "zk_user_id": 7},
    {"employee_no": "E008", "name": "吴海", "gender": "男", "phone": "13812340008", "department_id": 4, "position": "质检员", "entry_date": date(2025,8,15), "card_no": "60001008", "zk_user_id": 8},
]
emp_objs = []
for ed in emps:
    e = Employee(**ed, status="active", is_active=True, zk_password="123456")
    db.add(e)
    emp_objs.append(e)
db.flush()

shifts = [
    Shift(name="早班", shift_type="day", check_in_start=time(8,0), check_in_end=time(9,5), check_out_start=time(17,0), check_out_end=time(18,0), work_hours="8", color="#409EFF", is_active=True),
    Shift(name="中班", shift_type="middle", check_in_start=time(9,0), check_in_end=time(10,0), check_out_start=time(18,0), check_out_end=time(19,0), work_hours="8", color="#67C23A", is_active=True),
    Shift(name="夜班", shift_type="night", check_in_start=time(20,0), check_in_end=time(21,0), check_out_start=time(4,0), check_out_end=time(5,30), work_hours="8", color="#E6A23C", is_active=True),
]
db.add_all(shifts)
db.flush()

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
        db.add(AttendanceRecord(employee_id=emp.id, device_id=1, punch_date=d, punch_time=datetime(d.year,d.month,d.day,h_in,m_in,random.randint(0,59)), punch_type="check_in", verify_type=1, status=status_in))
        total_rec += 1
        h_out = random.choice([17,17,18,18,18,19])
        m_out = random.randint(0, 59)
        status_out = "early" if h_out < 17 else "normal"
        db.add(AttendanceRecord(employee_id=emp.id, device_id=1, punch_date=d, punch_time=datetime(d.year,d.month,d.day,h_out,m_out,random.randint(0,59)), punch_type="check_out", verify_type=1, status=status_out))
        total_rec += 1

db.commit()
print(f"Done: 1 device, {len(depts)} depts, {len(emp_objs)} emps, {len(shifts)} shifts, {total_rec} records")
