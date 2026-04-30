from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.employee import Employee
from app.models.department import Department

router = APIRouter(prefix="/roster", tags=["花名册"])


@router.get("/")
def list_roster(skip: int = 0, limit: int = 30, status: Optional[str] = None,
                employee_type: Optional[str] = None, keyword: Optional[str] = None,
                department: Optional[str] = None, factory: Optional[str] = None,
                search: Optional[str] = None, position: Optional[str] = None,
                db: Session = Depends(get_db)):
    """
    前端花名册页面和员工管理页面共用此接口。
    - employee_type -> employment_type (正式工/派遣工/退休返聘)
    - status -> is_active (all/employed/left) or person_type (正式工/派遣工/退休返聘)
    """
    from sqlalchemy import or_
    query = db.query(Employee)
    if status:
        if status == 'left':
            query = query.filter(Employee.is_active == False)
        elif status == 'employed':
            query = query.filter(Employee.is_active == True)
        elif status == 'probation':
            from datetime import date
            query = query.filter(Employee.probation_end_date != None,
                                 Employee.probation_end_date >= date.today())
        elif status in ('正式工', '派遣工', '退休返聘'):
            # 前端tab类型
            query = query.filter(Employee.employment_type == status)
        elif status != 'all':
            query = query.filter(Employee.status == status)
        # status == 'all' 时显示所有员工（在职+离职），不过滤 is_active
    else:
        query = query.filter(Employee.is_active == True)
    if employee_type:
        query = query.filter(Employee.employment_type == employee_type)
    if department:
        from app.models.department import Department
        dept = db.query(Department).filter(Department.name == department).first()
        if dept:
            query = query.filter(Employee.department_id == dept.id)
    if factory:
        query = query.filter(Employee.factory == factory)
    if keyword or search:
        q = keyword or search
        query = query.filter(or_(
            Employee.name.contains(q),
            Employee.employee_no.contains(q),
            Employee.phone.contains(q)
        ))
    if position:
        query = query.filter(Employee.position.contains(position))
    total = query.count()
    employees = query.offset(skip).limit(limit).all()
    return {"total": total, "items": [_emp_dict(e, db) for e in employees]}


@router.get("/departments")
def list_roster_departments(status: Optional[str] = None, db: Session = Depends(get_db)):
    """花名册页面用的部门列表（带员工计数）"""
    from app.models.employee import Employee
    depts = db.query(Department).all()
    result = []
    for d in depts:
        # 根据当前筛选状态计算员工数
        emp_query = db.query(Employee).filter(Employee.department_id == d.id)
        if status == 'employed':
            emp_query = emp_query.filter(Employee.is_active == True)
        elif status == 'left':
            emp_query = emp_query.filter(Employee.is_active == False)
        elif status == 'probation':
            from datetime import date
            emp_query = emp_query.filter(
                Employee.probation_end_date != None,
                Employee.probation_end_date >= date.today()
            )
        elif status in ('正式工', '派遣工', '退休返聘'):
            emp_query = emp_query.filter(Employee.employment_type == status)
        # status='all' 或 status=None 时统计所有员工
        count = emp_query.count()
        if count > 0:
            result.append({"id": d.id, "name": d.name, "employee_count": count})
    return result


@router.get("/positions")
def list_positions(status: Optional[str] = None, db: Session = Depends(get_db)):
    """花名册页面用的职位列表"""
    from app.models.employee import Employee
    emp_query = db.query(Employee.position).distinct().filter(Employee.position.isnot(None))
    if status == 'employed':
        emp_query = emp_query.filter(Employee.is_active == True)
    elif status == 'left':
        emp_query = emp_query.filter(Employee.is_active == False)
    elif status == 'probation':
        from datetime import date
        emp_query = emp_query.filter(
            Employee.probation_end_date != None,
            Employee.probation_end_date >= date.today()
        )
    elif status in ('正式工', '派遣工', '退休返聘'):
        emp_query = emp_query.filter(Employee.employment_type == status)
    positions = emp_query.all()
    return [{"position": p[0]} for p in positions]


def _emp_dict(emp, db: Session = None):
    from sqlalchemy import text
    # 从 roster 表获取真实入职次数
    entry_count = 1
    if db and emp.employee_no:
        try:
            result = db.execute(
                text("SELECT 入职次数 FROM roster WHERE 工号=:no"),
                {"no": emp.employee_no}
            ).fetchone()
            if result:
                entry_count = result[0]
        except Exception:
            pass
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
        "是否在职": 1 if emp.is_active else 0,
        "status": emp.status,
        "入职次数": entry_count,
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
    }


@router.get("/summary")
def get_roster_summary(db: Session = Depends(get_db)):
    """花名册统计：各用工形式人数、总人数"""
    total = db.query(Employee).filter(Employee.is_active == True).count()
    by_type = {}
    for t in ['正式工', '派遣工', '退休返聘', '实习生']:
        cnt = db.query(Employee).filter(
            Employee.is_active == True,
            Employee.employment_type == t
        ).count()
        by_type[t] = cnt
    return {"total": total, "by_type": by_type}


@router.get("/lookup")
def lookup_roster(q: str, db: Session = Depends(get_db)):
    """按姓名或工号搜索员工（花名册搜索框用），返回第一条匹配记录"""
    emp = db.query(Employee).filter(
        Employee.is_active == True,
        (Employee.name.contains(q)) | (Employee.employee_no.contains(q))
    ).first()
    if not emp:
        return None
    return _emp_dict(emp, db)
