"""部门休息时间配置 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.department_break import DepartmentBreak
from app.models.department import Department

router = APIRouter(prefix="/department-breaks", tags=["部门休息时间"])


class BreakCreate(BaseModel):
    department_id: int
    break_start: str
    break_end: str
    break_minutes: int


class BreakUpdate(BaseModel):
    break_start: Optional[str] = None
    break_end: Optional[str] = None
    break_minutes: Optional[int] = None


class BreakResponse(BaseModel):
    id: int
    department_id: int
    department_name: str
    break_start: str
    break_end: str
    break_minutes: int
    is_active: bool

    class Config:
        from_attributes = True


@router.get("/", response_model=List[BreakResponse])
def list_breaks(db: Session = Depends(get_db)):
    """获取所有部门的休息时间配置"""
    results = []
    breaks = db.query(DepartmentBreak).all()
    for b in breaks:
        dept = db.query(Department).filter(Department.id == b.department_id).first()
        results.append(BreakResponse(
            id=b.id,
            department_id=b.department_id,
            department_name=dept.name if dept else "未知",
            break_start=b.break_start,
            break_end=b.break_end,
            break_minutes=b.break_minutes,
            is_active=b.is_active,
        ))
    return results


@router.post("/", response_model=BreakResponse)
def create_or_update_break(data: BreakCreate, db: Session = Depends(get_db)):
    """配置部门的休息时间（没有则创建，有则更新）"""
    dept = db.query(Department).filter(Department.id == data.department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")

    br = db.query(DepartmentBreak).filter(DepartmentBreak.department_id == data.department_id).first()
    if br:
        br.break_start = data.break_start
        br.break_end = data.break_end
        br.break_minutes = data.break_minutes
    else:
        br = DepartmentBreak(
            department_id=data.department_id,
            break_start=data.break_start,
            break_end=data.break_end,
            break_minutes=data.break_minutes,
        )
        db.add(br)

    db.commit()
    db.refresh(br)
    return BreakResponse(
        id=br.id,
        department_id=br.department_id,
        department_name=dept.name,
        break_start=br.break_start,
        break_end=br.break_end,
        break_minutes=br.break_minutes,
        is_active=br.is_active,
    )


@router.put("/{department_id}", response_model=BreakResponse)
def update_break(department_id: int, data: BreakUpdate, db: Session = Depends(get_db)):
    """更新部门的休息时间"""
    br = db.query(DepartmentBreak).filter(DepartmentBreak.department_id == department_id).first()
    if not br:
        raise HTTPException(status_code=404, detail="该部门未配置休息时间")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(br, field, value)

    db.commit()
    db.refresh(br)
    dept = db.query(Department).filter(Department.id == department_id).first()
    return BreakResponse(
        id=br.id,
        department_id=br.department_id,
        department_name=dept.name if dept else "未知",
        break_start=br.break_start,
        break_end=br.break_end,
        break_minutes=br.break_minutes,
        is_active=br.is_active,
    )


@router.delete("/{department_id}")
def delete_break(department_id: int, db: Session = Depends(get_db)):
    """删除部门的休息时间配置"""
    br = db.query(DepartmentBreak).filter(DepartmentBreak.department_id == department_id).first()
    if not br:
        raise HTTPException(status_code=404, detail="该部门未配置休息时间")
    db.delete(br)
    db.commit()
    return {"message": "删除成功"}
