import os
import sys
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal
from app.models.employee import Employee
from datetime import datetime, date

db = SessionLocal()
employees = db.query(Employee).all()

fixed = 0
for emp in employees:
    changed = False
    
    # 修复科学计数法身份证号
    if emp.id_card and ('e+' in str(emp.id_card) or 'E+' in str(emp.id_card)):
        # 尝试从公式中提取
        if emp.gender and str(emp.gender).startswith('='):
            # 从公式如 =IF(MOD(MID(T48,17,1),2)=1,"男","女") 中无法恢复
            # 设置为未知
            emp.gender = None
            emp.id_card = None
            emp.age = None
            emp.birth_date = None
            changed = True
            print(f"Cleared bad data for ID {emp.id}: {emp.name}")
    
    # 修复仍有公式的gender
    if emp.gender and str(emp.gender).startswith('='):
        if emp.id_card and len(str(emp.id_card)) == 18:
            try:
                gender_code = int(str(emp.id_card)[16])
                emp.gender = "男" if gender_code % 2 == 1 else "女"
                changed = True
            except:
                emp.gender = None
                changed = True
        else:
            emp.gender = None
            changed = True
    
    # 修复异常年龄
    if emp.age and (emp.age > 100 or emp.age < 0):
        if emp.id_card and len(str(emp.id_card)) == 18:
            try:
                birth_year = int(str(emp.id_card)[6:10])
                birth_month = int(str(emp.id_card)[10:12])
                birth_day = int(str(emp.id_card)[12:14])
                today = date(2026, 4, 30)
                age = today.year - birth_year
                if (today.month, today.day) < (birth_month, birth_day):
                    age -= 1
                emp.age = max(0, age)
                changed = True
            except:
                emp.age = None
                changed = True
        else:
            emp.age = None
            changed = True
    
    if changed:
        fixed += 1

db.commit()
print(f"Fixed {fixed} employees with anomalies")
db.close()
