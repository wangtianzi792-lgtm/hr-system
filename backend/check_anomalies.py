import os
import sys
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal
from app.models.employee import Employee

db = SessionLocal()
employees = db.query(Employee).all()

print("Anomalies:")
for emp in employees:
    # 检查仍有公式的
    if emp.gender and str(emp.gender).startswith('='):
        print(f"  Formula gender: {emp.name} (ID:{emp.id}) - {emp.gender[:50]}")
    
    # 检查异常年龄
    if emp.age and (emp.age > 100 or emp.age < 0):
        print(f"  Bad age: {emp.name} (ID:{emp.id}) - age={emp.age}, id_card={emp.id_card}")
    
    # 检查身份证问题
    if emp.id_card and len(emp.id_card) != 18:
        print(f"  Bad id_card length: {emp.name} (ID:{emp.id}) - len={len(emp.id_card)}, card={emp.id_card}")

db.close()
