from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.employee import Employee
from app.models.department import Department
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.services.zk_service import ZKDeviceService

router = APIRouter(prefix="/employees", tags=["员工管理"])


def _emp_dict(emp, db=None):
    from app.models.role import Role  # 避免循环导入
    d = {"id": emp.id, "employee_no": emp.employee_no, "name": emp.name}
    for field in ['gender','phone','email','id_card','department_id','position',
                  'entry_date','status','card_no','zk_user_id','zk_password',
                  'is_active','created_at','updated_at','role_id',
                  # 海昌花名册扩展字段
                  'archive_no','factory','person_type','business_unit','process',
                  'medical_exam_type','medical_exam_factor','dept_audit','position_audit',
                  'job_level','probation_end_date','emergency_phone','birth_date','age',
                  'ethnicity','work_years','employment_type','medical_category',
                  'employee_group','education','education_salary','school_major',
                  'household_address','temporary_address','contract_start','contract_end',
                  'contract_signed','provident_fund','retirement_date','work_years_salary',
                  'training']:
        d[field] = getattr(emp, field, None)
    if emp.department:
        d['department_name'] = emp.department.name
    if emp.role_id and db:
        role = db.query(Role).filter(Role.id == emp.role_id).first()
        if role:
            d['role_name'] = role.display_name
    return d


@router.post("/")
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    existing = db.query(Employee).filter(Employee.employee_no == employee.employee_no).first()
    if existing:
        raise HTTPException(status_code=400, detail="工号已存在")
    db_emp = Employee(**employee.model_dump(exclude_none=True))
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return _emp_dict(db_emp, db)


@router.get("/")
def list_employees(skip: int = 0, limit: int = 100, department_id: Optional[int] = None,
                  keyword: Optional[str] = None, status: Optional[str] = None,
                  factory: Optional[str] = None, person_type: Optional[str] = None,
                  db: Session = Depends(get_db)):
    from sqlalchemy import or_
    query = db.query(Employee)
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    if status:
        query = query.filter(Employee.status == status)
    if factory:
        query = query.filter(Employee.factory == factory)
    if person_type:
        query = query.filter(Employee.person_type == person_type)
    if keyword:
        query = query.filter(or_(Employee.name.contains(keyword),
                                Employee.employee_no.contains(keyword),
                                Employee.phone.contains(keyword)))
    total = query.count()
    employees = query.offset(skip).limit(limit).all()
    return {"total": total, "items": [_emp_dict(e, db) for e in employees]}


@router.get("/{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    return _emp_dict(emp, db)


@router.put("/{employee_id}")
def update_employee(employee_id: int, data: EmployeeUpdate, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    for field, value in data.model_dump(exclude_none=True).items():
        if field == 'entry_date' and value:
            from datetime import date
            if isinstance(value, str):
                value = date.fromisoformat(value)
        setattr(emp, field, value)
    db.commit()
    db.refresh(emp)
    return _emp_dict(emp, db)


@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    db.delete(emp)
    db.commit()
    return {"message": "员工删除成功"}


@router.post("/{employee_id}/enroll")
def enroll_employee(employee_id: int, device_id: int, db: Session = Depends(get_db)):
    from app.models.device import Device
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    try:
        with ZKDeviceService(device.ip_address, device.port) as zk:
            success = zk.set_user(user_id=str(emp.id), name=emp.name,
                                  password=emp.zk_password or "", privilege=0)
            if success:
                emp.zk_user_id = emp.id
                db.commit()
                return {"message": "员工已下发到考勤机", "zk_user_id": emp.id}
            raise HTTPException(status_code=500, detail="下发失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下发失败: {str(e)}")


@router.post("/{employee_id}/remove-from-device")
def remove_from_device(employee_id: int, device_id: int, db: Session = Depends(get_db)):
    from app.models.device import Device
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    try:
        with ZKDeviceService(device.ip_address, device.port) as zk:
            if emp.zk_user_id:
                zk.delete_user(user_id=str(emp.zk_user_id))
                emp.zk_user_id = None
                db.commit()
            return {"message": "员工已从考勤机移除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"移除失败: {str(e)}")