# -*- coding: utf-8 -*-
"""修复员工数据中的Excel公式污染"""
import os
import sys
from datetime import datetime, date

backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal
from app.models.employee import Employee

def calculate_gender(id_card):
    if not id_card or len(id_card) < 17:
        return None
    try:
        gender_code = int(id_card[16])
        return "男" if gender_code % 2 == 1 else "女"
    except:
        return None

def calculate_work_years(entry_date):
    if not entry_date:
        return None
    try:
        if isinstance(entry_date, str):
            entry_date = datetime.strptime(entry_date, "%Y-%m-%d").date()
        today = date(2026, 4, 30)
        years = today.year - entry_date.year
        if (today.month, today.day) < (entry_date.month, entry_date.day):
            years -= 1
        return max(0, years)
    except:
        return None

def calculate_work_years_salary(work_years):
    if work_years is None:
        return "0"
    return str(min(work_years * 50, 500))

def calculate_age(id_card):
    if not id_card or len(id_card) < 14:
        return None
    try:
        birth_year = int(id_card[6:10])
        birth_month = int(id_card[10:12])
        birth_day = int(id_card[12:14])
        today = date(2026, 4, 30)
        age = today.year - birth_year
        if (today.month, today.day) < (birth_month, birth_day):
            age -= 1
        return max(0, age)
    except:
        return None

def parse_birth_date(id_card):
    if not id_card or len(id_card) < 14:
        return None
    try:
        return date(int(id_card[6:10]), int(id_card[10:12]), int(id_card[12:14]))
    except:
        return None

def get_medical_exam_type(age):
    if age is None:
        return "普通体检"
    if age >= 45:
        return "45岁以上体检"
    elif age >= 35:
        return "35-45岁体检"
    else:
        return "普通体检"

def is_formula(val):
    if val is None:
        return False
    if isinstance(val, str) and val.startswith('='):
        return True
    return False

db = SessionLocal()
try:
    employees = db.query(Employee).all()
    print(f"Total employees: {len(employees)}")
    
    fixed_count = 0
    for emp in employees:
        changed = False
        
        # 修复性别
        if not emp.gender or is_formula(emp.gender):
            new_gender = calculate_gender(emp.id_card)
            if new_gender:
                emp.gender = new_gender
                changed = True
        
        # 修复出生日期
        if emp.birth_date is None or is_formula(emp.birth_date):
            new_birth = parse_birth_date(emp.id_card)
            if new_birth:
                emp.birth_date = new_birth
                changed = True
        
        # 修复年龄
        if emp.age is None or is_formula(emp.age):
            new_age = calculate_age(emp.id_card)
            if new_age is not None:
                emp.age = new_age
                changed = True
        
        # 修复工龄
        if emp.work_years is None or is_formula(emp.work_years):
            new_years = calculate_work_years(emp.entry_date)
            if new_years is not None:
                emp.work_years = str(new_years)
                changed = True
        
        # 修复工龄工资
        if emp.work_years_salary is None or is_formula(emp.work_years_salary):
            years = None
            if emp.work_years and not is_formula(emp.work_years):
                try:
                    years = int(emp.work_years)
                except:
                    years = calculate_work_years(emp.entry_date)
            else:
                years = calculate_work_years(emp.entry_date)
            emp.work_years_salary = calculate_work_years_salary(years)
            changed = True
        
        # 修复体检类别
        if not emp.medical_exam_type or is_formula(emp.medical_exam_type):
            age = emp.age if emp.age and not is_formula(emp.age) else calculate_age(emp.id_card)
            emp.medical_exam_type = get_medical_exam_type(age)
            changed = True
        
        if changed:
            fixed_count += 1
    
    db.commit()
    print(f"Fixed {fixed_count} employees")
    
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
