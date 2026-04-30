import os
import sys
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal
from app.models.employee import Employee

db = SessionLocal()
employees = db.query(Employee).all()

print(f"Total employees: {len(employees)}")
print("\nChecking for formula corruption...")

formula_fields = ['gender', 'medical_exam_type', 'work_years', 'work_years_salary', 'education_salary']
corrupted_count = 0

for emp in employees[:10]:
    corrupted = []
    for field in formula_fields:
        val = getattr(emp, field)
        if val and isinstance(val, str) and val.startswith('='):
            corrupted.append(f"{field}={val[:30]}...")
    if corrupted:
        corrupted_count += 1
        print(f"  {emp.name} ({emp.employee_no}): {', '.join(corrupted)}")

print(f"\nChecked 10 employees, {corrupted_count} corrupted")
db.close()
