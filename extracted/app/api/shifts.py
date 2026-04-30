"""排班管理 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, text
from typing import List, Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel, model_validator
from typing import Union
import logging

from app.core.database import get_db
from app.models.scheduling import Shift, ShiftAssignment, ScheduleRecord
from app.models.leave import LeaveRequest, OvertimeRequest, AttendanceRule
from app.models.employee import Employee
from app.models.department import Department
from app.models.user import User

router = APIRouter(prefix="/shifts", tags=["班次管理"])
logger = logging.getLogger(__name__)


# ---- Pydantic schemas ----

class ShiftCreate(BaseModel):
    name: str
    shift_type: str = "day"
    check_in_start: str
    check_in_end: str
    check_out_start: str
    check_out_end: str
    work_hours: Union[int, float, str, None] = None
    color: Optional[str] = "#409EFF"
    remark: Optional[str] = None

    @model_validator(mode="before")
    def coerce_work_hours(cls, v):
        if isinstance(v, dict) and "work_hours" in v:
            wh = v["work_hours"]
            if isinstance(wh, (int, float)):
                v["work_hours"] = str(wh)
        return v


class ShiftUpdate(BaseModel):
    name: Optional[str] = None
    shift_type: Optional[str] = None
    check_in_start: Optional[str] = None
    check_in_end: Optional[str] = None
    check_out_start: Optional[str] = None
    check_out_end: Optional[str] = None
    work_hours: Union[int, float, str, None] = None
    color: Optional[str] = None
    remark: Optional[str] = None
    is_active: Optional[bool] = None

    @model_validator(mode="before")
    def coerce_work_hours(cls, v):
        if isinstance(v, dict) and "work_hours" in v:
            wh = v["work_hours"]
            if isinstance(wh, (int, float)):
                v["work_hours"] = str(wh)
        return v


class ShiftAssignCreate(BaseModel):
    employee_id: int
    shift_id: int
    start_date: str
    end_date: Optional[str] = None
    week_days: Optional[str] = None  # "1,2,3,4,5" etc.


class ScheduleCreate(BaseModel):
    employee_id: int
    schedule_date: str
    shift_id: Optional[int] = None
    status: Optional[str] = "scheduled"


class BatchScheduleCreate(BaseModel):
    department_ids: Optional[List[int]] = None
    employee_ids: Optional[List[int]] = None
    start_date: str
    end_date: str
    shift_id: Optional[int] = None
    week_days: Optional[str] = None


# ---- 班次 CRUD ----

@router.get("/")
def list_shifts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    total = db.query(Shift).count()
    items = db.query(Shift).order_by(Shift.id.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [_shift_to_dict(s) for s in items]}


@router.post("/")
def create_shift(data: ShiftCreate, db: Session = Depends(get_db)):
    from datetime import time as dt_time
    ci_s = datetime.strptime(data.check_in_start, "%H:%M").time()
    ci_e = datetime.strptime(data.check_in_end, "%H:%M").time()
    co_s = datetime.strptime(data.check_out_start, "%H:%M").time()
    co_e = datetime.strptime(data.check_out_end, "%H:%M").time()
    shift = Shift(
        name=data.name,
        shift_type=data.shift_type,
        check_in_start=ci_s,
        check_in_end=ci_e,
        check_out_start=co_s,
        check_out_end=co_e,
        work_hours=data.work_hours,
        color=data.color,
        remark=data.remark,
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return _shift_to_dict(shift)


@router.put("/{shift_id}")
def update_shift(shift_id: int, data: ShiftUpdate, db: Session = Depends(get_db)):
    from datetime import time as dt_time
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="班次不存在")
    for field, value in data.model_dump(exclude_unset=True).items():
        if field in ("check_in_start", "check_in_end", "check_out_start", "check_out_end") and value:
            try:
                # 处理 24:00 这种边界值，转为 00:00
                parsed = datetime.strptime(value.replace("24:00", "00:00"), "%H:%M")
                setattr(shift, field, parsed.time())
            except ValueError:
                raise HTTPException(status_code=422, detail=f"时间字段 {field} 格式无效：{value}，正确格式如 09:00")
        elif field == "is_active":
            setattr(shift, field, value)
        elif value is not None:
            setattr(shift, field, value)
    db.commit()
    return _shift_to_dict(shift)


@router.delete("/{shift_id}")
def delete_shift(shift_id: int, db: Session = Depends(get_db)):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="班次不存在")
    db.delete(shift)
    db.commit()
    return {"message": "删除成功"}


# ---- 班次分配 ----

@router.post("/assign")
def assign_shift(data: ShiftAssignCreate, db: Session = Depends(get_db)):
    # 先删除该员工同日期范围的旧分配
    db.query(ShiftAssignment).filter(
        ShiftAssignment.employee_id == data.employee_id
    ).delete()
    assign = ShiftAssignment(
        employee_id=data.employee_id,
        shift_id=data.shift_id,
        start_date=data.start_date,
        end_date=data.end_date,
        week_days=data.week_days,
    )
    db.add(assign)
    db.commit()
    return {"message": "分配成功"}


@router.get("/assignments")
def list_assignments(employee_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(ShiftAssignment).options(joinedload(ShiftAssignment.employee), joinedload(ShiftAssignment.shift))
    if employee_id:
        query = query.filter(ShiftAssignment.employee_id == employee_id)
    items = query.all()
    return {
        "total": len(items),
        "items": [{
            "id": a.id,
            "employee_id": a.employee_id,
            "employee_name": a.employee.name if a.employee else "",
            "shift_id": a.shift_id,
            "shift_name": a.shift.name if a.shift else "",
            "start_date": a.start_date,
            "end_date": a.end_date,
            "week_days": a.week_days,
            "is_active": a.is_active,
        } for a in items]
    }


# ---- 排班记录 ----

@router.get("/schedules")
def list_schedules(
    employee_id: Optional[int] = None,
    department_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(ScheduleRecord).options(joinedload(ScheduleRecord.employee))
    if employee_id:
        query = query.filter(ScheduleRecord.employee_id == employee_id)
    if start_date:
        query = query.filter(ScheduleRecord.schedule_date >= start_date)
    if end_date:
        query = query.filter(ScheduleRecord.schedule_date <= end_date)
    total = query.count()
    items = query.order_by(ScheduleRecord.schedule_date.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "items": [{
            "id": s.id,
            "employee_id": s.employee_id,
            "employee_name": s.employee.name if s.employee else "",
            "schedule_date": s.schedule_date,
            "shift_id": s.shift_id,
            "shift_name": s.shift_name,
            "status": s.status,
            "remark": s.remark,
        } for s in items]
    }


@router.post("/schedules")
def create_schedule(data: ScheduleCreate, db: Session = Depends(get_db)):
    shift_obj = db.query(Shift).filter(Shift.id == data.shift_id).first() if data.shift_id else None
    record = ScheduleRecord(
        employee_id=data.employee_id,
        schedule_date=data.schedule_date,
        shift_id=data.shift_id,
        shift_name=shift_obj.name if shift_obj else None,
        shift_type=shift_obj.shift_type if shift_obj else None,
        check_in_start=shift_obj.check_in_start if shift_obj else None,
        check_in_end=shift_obj.check_in_end if shift_obj else None,
        check_out_start=shift_obj.check_out_start if shift_obj else None,
        check_out_end=shift_obj.check_out_end if shift_obj else None,
        status=data.status or "scheduled",
    )
    db.add(record)
    db.commit()
    return {"message": "排班创建成功"}


@router.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    record = db.query(ScheduleRecord).filter(ScheduleRecord.id == schedule_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="排班记录不存在")
    db.delete(record)
    db.commit()
    return {"message": "删除成功"}


@router.post("/schedules/batch")
def batch_schedule(data: BatchScheduleCreate, db: Session = Depends(get_db)):
    """批量排班：给部门或员工批量安排某时间段内的班次"""
    # 确定目标员工
    if data.employee_ids:
        employees = db.query(Employee).filter(Employee.id.in_(data.employee_ids)).all()
    elif data.department_ids:
        employees = db.query(Employee).filter(
            Employee.department_id.in_(data.department_ids),
            Employee.is_active == True
        ).all()
    else:
        raise HTTPException(status_code=400, detail="请指定部门或员工")
    
    shift_obj = db.query(Shift).filter(Shift.id == data.shift_id).first() if data.shift_id else None
    
    start = datetime.strptime(data.start_date, "%Y-%m-%d").date()
    end = datetime.strptime(data.end_date, "%Y-%m-%d").date()
    
    created = 0
    for emp in employees:
        d = start
        while d <= end:
            # 周几筛选
            if data.week_days and str(d.weekday()) not in data.week_days.split(","):
                d += timedelta(days=1)
                continue
            
            # 检查是否已有排班
            existing = db.query(ScheduleRecord).filter(
                ScheduleRecord.employee_id == emp.id,
                ScheduleRecord.schedule_date == str(d)
            ).first()
            if existing:
                if shift_obj:
                    existing.shift_id = shift_obj.id
                    existing.shift_name = shift_obj.name
                    existing.shift_type = shift_obj.shift_type
                    existing.check_in_start = shift_obj.check_in_start
                    existing.check_in_end = shift_obj.check_in_end
                    existing.check_out_start = shift_obj.check_out_start
                    existing.check_out_end = shift_obj.check_out_end
                    existing.auto_generated = True
                d += timedelta(days=1)
                continue
            
            record = ScheduleRecord(
                employee_id=emp.id,
                schedule_date=str(d),
                shift_id=shift_obj.id if shift_obj else None,
                shift_name=shift_obj.name if shift_obj else None,
                shift_type=shift_obj.shift_type if shift_obj else None,
                check_in_start=shift_obj.check_in_start if shift_obj else None,
                check_in_end=shift_obj.check_in_end if shift_obj else None,
                check_out_start=shift_obj.check_out_start if shift_obj else None,
                check_out_end=shift_obj.check_out_end if shift_obj else None,
                status="scheduled",
                auto_generated=True,
            )
            db.add(record)
            created += 1
            d += timedelta(days=1)
    
    db.commit()
    return {"message": f"批量排班完成，共创建 {created} 条记录"}


def _shift_to_dict(s: Shift) -> dict:
    return {
        "id": s.id,
        "name": s.name,
        "shift_type": s.shift_type,
        "check_in_start": s.check_in_start.strftime("%H:%M") if s.check_in_start else None,
        "check_in_end": s.check_in_end.strftime("%H:%M") if s.check_in_end else None,
        "check_out_start": s.check_out_start.strftime("%H:%M") if s.check_out_start else None,
        "check_out_end": s.check_out_end.strftime("%H:%M") if s.check_out_end else None,
        "work_hours": s.work_hours,
        "color": s.color,
        "remark": s.remark,
        "is_active": s.is_active,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }