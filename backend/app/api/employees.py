from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.employee import Employee
from app.models.department import Department
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.services.zk_service import ZKDeviceService

router = APIRouter(prefix="/employees", tags=["员工管理"])


def _emp_dict(emp):
    return {
        "id": emp.id,
        "工号": emp.employee_no,
        "姓名": emp.name,
        "性别": emp.gender,
        "部门": emp.department.name if emp.department else None,
        "岗位": emp.position,
        "职务级别": emp.job_level,
        "用工形式": emp.employment_type,
        "厂区": emp.factory,
        "事业部": emp.business_unit,
        "工序": emp.process,
        "入职时间": emp.entry_date,
        "联系电话": emp.phone,
        "身份证号": emp.id_card,
        "年龄": emp.age,
        "民族": emp.ethnicity,
        "文化程度": emp.education,
        "学历工资": emp.education_salary,
        "工龄": emp.work_years,
        "工龄工资": emp.work_years_salary,
        "合同起始": emp.contract_start,
        "合同终止": emp.contract_end,
        "签定": emp.contract_signed,
        "公积金标准": emp.provident_fund,
        "体检类别": emp.medical_exam_type,
        "is_active": emp.is_active,
        "status": emp.status,
        "是否在职": 1 if emp.is_active else 0,
        "入职次数": 1,
        "户籍地址": emp.household_address,
        "扬州暂住地": emp.temporary_address,
        "毕业院校及专业": emp.school_major,
        "档案号": emp.archive_no,
        "试用到期日": emp.probation_end_date,
        "紧急联系电话": emp.emergency_phone,
        "出生日期": emp.birth_date,
        "劳务公司": None,
        "退休人员日期": emp.retirement_date,
        "参加培训": emp.training,
        "person_type": emp.person_type,
    }


@router.post("/")
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    existing = db.query(Employee).filter(Employee.employee_no == employee.employee_no).first()
    if existing:
        raise HTTPException(status_code=400, detail="工号已存在")
    db_emp = Employee(**employee.model_dump(exclude_none=True))
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return _emp_dict(db_emp)


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
        if status == 'left':
            query = query.filter(Employee.is_active == False)
        elif status == 'employed':
            query = query.filter(Employee.is_active == True)
        elif status == 'probation':
            from datetime import date
            query = query.filter(Employee.probation_end_date != None,
                                 Employee.probation_end_date >= date.today())
        elif status != 'all':
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
    return {"total": total, "items": [_emp_dict(e) for e in employees]}


@router.get("/export")
def export_employees(
    department_id: Optional[int] = None,
    status: Optional[str] = None,
    employment_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """导出员工Excel"""
    query_obj = db.query(Employee)
    if department_id:
        query_obj = query_obj.filter(Employee.department_id == department_id)
    if status == 'active':
        query_obj = query_obj.filter(Employee.is_active == True)
    elif status == 'inactive':
        query_obj = query_obj.filter(Employee.is_active == False)
    if employment_type:
        query_obj = query_obj.filter(Employee.employment_type == employment_type)

    employees = query_obj.all()

    # 生成CSV
    import csv
    import io
    output = io.StringIO()
    headers = ["工号", "姓名", "性别", "部门", "岗位", "职务级别", "用工形式",
               "入职时间", "联系电话", "身份证号", "年龄", "民族", "在册状态"]
    writer = csv.writer(output)
    writer.writerow(headers)
    for e in employees:
        writer.writerow([
            e.employee_no, e.name, e.gender,
            e.department.name if e.department else "",
            e.position, e.job_level, e.employment_type,
            e.entry_date, e.phone, e.id_card,
            e.age, e.ethnicity,
            "在职" if e.is_active else "离职"
        ])

    from fastapi.responses import StreamingResponse
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=employees.csv"}
    )


@router.get("/{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    return _emp_dict(emp)


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
    return _emp_dict(emp)


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