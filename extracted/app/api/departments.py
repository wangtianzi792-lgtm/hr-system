"""部门管理 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import logging

from app.core.database import get_db
from app.models.department import Department
from app.models.employee import Employee
from app.schemas.department import (
    DepartmentCreate, DepartmentUpdate,
    DepartmentResponse, DepartmentTreeResponse
)

router = APIRouter(prefix="/departments", tags=["部门管理"])
logger = logging.getLogger(__name__)


def _dept_to_response(dept: Department, db: Session) -> dict:
    result = {
        "id": dept.id,
        "name": dept.name,
        "code": dept.code,
        "parent_id": dept.parent_id,
        "manager_id": dept.manager_id,
        "description": dept.description,
        "sort_order": dept.sort_order,
        "is_active": dept.is_active,
        "created_at": dept.created_at,
        "updated_at": dept.updated_at,
    }
    if dept.parent_id:
        parent = db.query(Department).filter(Department.id == dept.parent_id).first()
        if parent:
            result["parent_name"] = parent.name
    if dept.manager_id:
        manager = db.query(Employee).filter(Employee.id == dept.manager_id).first()
        if manager:
            result["manager_name"] = manager.name
    # 员工数量
    count = db.query(func.count(Employee.id)).filter(Employee.department_id == dept.id).scalar()
    result["employee_count"] = count or 0
    return result


def _build_tree(departments: List[Department]) -> List[dict]:
    """将扁平部门列表转为树形结构"""
    lookup = {d.id: {"id": d.id, "name": d.name, "code": d.code,
                      "parent_id": d.parent_id, "sort_order": d.sort_order,
                      "is_active": d.is_active, "children": []}
              for d in departments}
    roots = []
    for d in departments:
        node = lookup[d.id]
        if d.parent_id and d.parent_id in lookup:
            lookup[d.parent_id]["children"].append(node)
        else:
            roots.append(node)
    # 按 sort_order 排序
    def sort_nodes(nodes):
        nodes.sort(key=lambda x: x["sort_order"])
        for n in nodes:
            sort_nodes(n["children"])
    sort_nodes(roots)
    return roots


@router.post("/", response_model=DepartmentResponse)
def create_department(dept: DepartmentCreate, db: Session = Depends(get_db)):
    """添加部门"""
    if dept.code:
        existing = db.query(Department).filter(Department.code == dept.code).first()
        if existing:
            raise HTTPException(status_code=400, detail="部门编码已存在")
    db_dept = Department(**dept.dict())
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return _dept_to_response(db_dept, db)


@router.get("/", response_model=List[DepartmentResponse])
def list_departments(
    keyword: Optional[str] = None,
    is_active: Optional[int] = None,
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db)
):
    """获取部门列表（扁平）"""
    query = db.query(Department)
    if keyword:
        query = query.filter(Department.name.contains(keyword) | Department.code.contains(keyword))
    if is_active is not None:
        query = query.filter(Department.is_active == is_active)

    depts = query.order_by(Department.sort_order.asc()).offset(skip).limit(limit).all()
    return [_dept_to_response(d, db) for d in depts]


@router.get("/tree", response_model=List[dict])
def get_department_tree(db: Session = Depends(get_db)):
    """获取部门树形结构"""
    depts = db.query(Department).filter(Department.is_active == 1).order_by(Department.sort_order.asc()).all()
    return _build_tree(depts)


@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(department_id: int, db: Session = Depends(get_db)):
    """获取部门详情"""
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    return _dept_to_response(dept, db)


@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(department_id: int, dept_update: DepartmentUpdate, db: Session = Depends(get_db)):
    """更新部门"""
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")

    if dept_update.code and dept_update.code != dept.code:
        existing = db.query(Department).filter(Department.code == dept_update.code, Department.id != department_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="部门编码已存在")

    # 禁止将自己设为自己的父级
    if dept_update.parent_id == department_id:
        raise HTTPException(status_code=400, detail="不能将自己设为上级部门")

    for field, value in dept_update.dict(exclude_unset=True).items():
        setattr(dept, field, value)

    db.commit()
    db.refresh(dept)
    return _dept_to_response(dept, db)


@router.delete("/{department_id}")
def delete_department(department_id: int, db: Session = Depends(get_db)):
    """删除部门（需确认无子部门且无员工）"""
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")

    # 检查是否有子部门
    children = db.query(Department).filter(Department.parent_id == department_id).first()
    if children:
        raise HTTPException(status_code=400, detail="请先删除子部门")

    # 检查是否有员工
    emp_count = db.query(func.count(Employee.id)).filter(Employee.department_id == department_id).scalar()
    if emp_count > 0:
        raise HTTPException(status_code=400, detail=f"该部门还有 {emp_count} 名员工，无法删除")

    db.delete(dept)
    db.commit()
    return {"message": "部门删除成功"}


@router.get("/{department_id}/employees")
def get_department_employees(department_id: int, db: Session = Depends(get_db)):
    """获取部门下的员工列表"""
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    employees = db.query(Employee).filter(Employee.department_id == department_id).all()
    return {"department_name": dept.name, "employee_count": len(employees),
            "employees": [{"id": e.id, "name": e.name, "employee_no": e.employee_no,
                           "position": e.position, "status": e.status} for e in employees]}
