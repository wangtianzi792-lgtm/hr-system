"""请假/加班/考勤规则 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.models.leave import LeaveRequest, OvertimeRequest, AttendanceRule
from app.models.employee import Employee
from app.models.user import User
from app.api.notification import create_notification

router = APIRouter(prefix="/leave", tags=["请假加班"])
logger = logging.getLogger(__name__)


# ---- 请假 schemas ----

class LeaveRequestCreate(BaseModel):
    employee_id: int
    leave_type: str
    start_date: str
    end_date: str
    total_days: int
    reason: Optional[str] = None


class LeaveRequestUpdate(BaseModel):
    leave_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_days: Optional[int] = None
    reason: Optional[str] = None
    status: Optional[str] = None


class OvertimeCreate(BaseModel):
    employee_id: int
    date: str
    start_time: str
    end_time: str
    hours: Optional[str] = None
    reason: Optional[str] = None


# ---- 请假 CRUD ----

@router.get("/")
def list_leave_requests(
    employee_id: Optional[int] = None,
    leave_type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(LeaveRequest).options(joinedload(LeaveRequest.employee), joinedload(LeaveRequest.approver))
    if employee_id:
        query = query.filter(LeaveRequest.employee_id == employee_id)
    if leave_type:
        query = query.filter(LeaveRequest.leave_type == leave_type)
    if status:
        query = query.filter(LeaveRequest.status == status)
    if start_date:
        query = query.filter(LeaveRequest.start_date >= start_date)
    if end_date:
        query = query.filter(LeaveRequest.end_date <= end_date)
    total = query.count()
    items = query.order_by(LeaveRequest.created_at.desc()).offset(skip).limit(limit).all()
    result = []
    for lr in items:
        result.append({
            "id": lr.id,
            "employee_id": lr.employee_id,
            "employee_name": lr.employee.name if lr.employee else "",
            "employee_no": lr.employee.employee_no if lr.employee else "",
            "department_name": lr.employee.department.name if lr.employee and lr.employee.department else "",
            "leave_type": lr.leave_type,
            "start_date": str(lr.start_date),
            "end_date": str(lr.end_date),
            "total_days": lr.total_days,
            "reason": lr.reason,
            "status": lr.status,
            "approver_id": lr.approver_id,
            "approver_name": lr.approver.name if lr.approver else "",
            "approve_comment": lr.approve_comment,
            "approve_time": lr.approve_time.isoformat() if lr.approve_time else None,
            "created_at": lr.created_at.isoformat() if lr.created_at else None,
        })
    return {"total": total, "items": result}


@router.post("/")
def create_leave_request(data: LeaveRequestCreate, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    lr = LeaveRequest(
        employee_id=data.employee_id,
        leave_type=data.leave_type,
        start_date=datetime.strptime(data.start_date, "%Y-%m-%d").date(),
        end_date=datetime.strptime(data.end_date, "%Y-%m-%d").date(),
        total_days=data.total_days,
        reason=data.reason,
    )
    db.add(lr)
    db.commit()
    return {"message": "请假申请提交成功", "id": lr.id}


@router.put("/{leave_id}")
def update_leave_request(leave_id: int, data: LeaveRequestUpdate, db: Session = Depends(get_db)):
    lr = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not lr:
        raise HTTPException(status_code=404, detail="请假记录不存在")
    for field, value in data.model_dump(exclude_unset=True).items():
        if field in ("start_date", "end_date") and value:
            setattr(lr, field, datetime.strptime(value, "%Y-%m-%d").date())
        elif value is not None:
            setattr(lr, field, value)
    db.commit()
    return {"message": "更新成功"}


@router.delete("/{leave_id}")
def delete_leave_request(leave_id: int, db: Session = Depends(get_db)):
    lr = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not lr:
        raise HTTPException(status_code=404, detail="请假记录不存在")
    if lr.status != "pending":
        raise HTTPException(status_code=400, detail="只能删除待审批的请假")
    db.delete(lr)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{leave_id}/cancel")
def cancel_leave_request(leave_id: int, db: Session = Depends(get_db)):
    """员工撤回自己的请假申请（仅待审批状态可撤回）"""
    lr = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not lr:
        raise HTTPException(status_code=404, detail="请假记录不存在")
    if lr.status != "pending":
        raise HTTPException(status_code=400, detail="只能撤回待审批的请假")
    lr.status = "cancelled"
    db.commit()
    return {"message": "请假已撤回"}


@router.post("/{leave_id}/approve")
def approve_leave_request(leave_id: int, approved: bool, comment: Optional[str] = None, db: Session = Depends(get_db)):
    lr = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not lr:
        raise HTTPException(status_code=404, detail="请假记录不存在")
    if lr.status != "pending":
        raise HTTPException(status_code=400, detail="该请假已审批")
    lr.status = "approved" if approved else "rejected"
    lr.approve_time = datetime.now()
    if comment:
        lr.approve_comment = comment
    db.commit()

    # 创建通知，告知申请人审批结果
    emp = db.query(Employee).filter(Employee.id == lr.employee_id).first()
    user_id = getattr(emp, 'user_id', None) if emp else None
    if user_id:
        leave_type_names = {
            "annual": "年假", "sick": "病假", "personal": "事假",
            "marriage": "婚假", "maternity": "产假", "bereavement": "丧假", "other": "其他"
        }
        type_name = leave_type_names.get(lr.leave_type, lr.leave_type)
        result = "批准" if approved else "拒绝"
        create_notification(
            db=db,
            user_id=user_id,
            title=f"请假申请{result}",
            content=f"您的{lr.total_days}天{type_name}申请（{lr.start_date} 至 {lr.end_date}）已被{'批准' if approved else '拒绝'}。",
            type="leave",
            related_id=lr.id,
            related_type="leave_request",
        )

    msg = "请假已批准" if approved else "请假已拒绝"
    return {"message": msg}


# ---- 加班 CRUD ----

@router.get("/overtime")
def list_overtime(
    employee_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(OvertimeRequest).options(joinedload(OvertimeRequest.employee))
    if employee_id:
        query = query.filter(OvertimeRequest.employee_id == employee_id)
    if status:
        query = query.filter(OvertimeRequest.status == status)
    if start_date:
        query = query.filter(OvertimeRequest.date >= start_date)
    if end_date:
        query = query.filter(OvertimeRequest.date <= end_date)
    total = query.count()
    items = query.order_by(OvertimeRequest.created_at.desc()).offset(skip).limit(limit).all()
    result = []
    for ot in items:
        result.append({
            "id": ot.id,
            "employee_id": ot.employee_id,
            "employee_name": ot.employee.name if ot.employee else "",
            "employee_no": ot.employee.employee_no if ot.employee else "",
            "date": str(ot.date),
            "start_time": ot.start_time,
            "end_time": ot.end_time,
            "hours": ot.hours,
            "reason": ot.reason,
            "status": ot.status,
            "approve_comment": ot.approve_comment,
            "created_at": ot.created_at.isoformat() if ot.created_at else None,
        })
    return {"total": total, "items": result}


@router.post("/overtime")
def create_overtime(data: OvertimeCreate, db: Session = Depends(get_db)):
    ot = OvertimeRequest(
        employee_id=data.employee_id,
        date=datetime.strptime(data.date, "%Y-%m-%d").date(),
        start_time=data.start_time,
        end_time=data.end_time,
        hours=data.hours,
        reason=data.reason,
    )
    db.add(ot)
    db.commit()
    return {"message": "加班申请提交成功", "id": ot.id}


@router.post("/overtime/{overtime_id}/approve")
def approve_overtime(overtime_id: int, approved: bool, comment: Optional[str] = None, db: Session = Depends(get_db)):
    ot = db.query(OvertimeRequest).filter(OvertimeRequest.id == overtime_id).first()
    if not ot:
        raise HTTPException(status_code=404, detail="加班记录不存在")
    ot.status = "approved" if approved else "rejected"
    ot.approve_time = datetime.now()
    if comment:
        ot.approve_comment = comment
    db.commit()
    msg = "加班已批准" if approved else "加班已拒绝"
    return {"message": msg}


# ---- 考勤规则 ----

@router.get("/rules")
def get_rules(db: Session = Depends(get_db)):
    rules = db.query(AttendanceRule).all()
    return {
        "items": [{
            "rule_key": r.rule_key,
            "rule_name": r.rule_name,
            "rule_value": r.rule_value,
            "remark": r.remark,
            "is_active": r.is_active,
        } for r in rules]
    }


@router.put("/rules")
def update_rules(rules_data: List[dict], db: Session = Depends(get_db)):
    for rd in rules_data:
        rule = db.query(AttendanceRule).filter(AttendanceRule.rule_key == rd["rule_key"]).first()
        if rule:
            rule.rule_value = rd.get("rule_value", rule.rule_value)
            rule.is_active = rd.get("is_active", rule.is_active)
        else:
            rule = AttendanceRule(
                rule_key=rd["rule_key"],
                rule_name=rd["rule_name"],
                rule_value=rd.get("rule_value"),
                remark=rd.get("remark"),
                is_active=rd.get("is_active", True),
            )
            db.add(rule)
    db.commit()
    return {"message": "规则更新成功"}


# ---- 假期余额 ----

@router.get("/balance/{employee_id}")
def get_leave_balance(employee_id: int, year: Optional[int] = None, db: Session = Depends(get_db)):
    """获取员工某年的假期余额"""
    if not year:
        year = datetime.now().year
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    
    approved_days = db.query(func.coalesce(func.sum(LeaveRequest.total_days), 0)).filter(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.status == "approved",
        LeaveRequest.leave_type.in_(["年假", "病假"]),
        LeaveRequest.start_date >= start,
        LeaveRequest.end_date <= end,
    ).scalar()
    
    return {
        "employee_id": employee_id,
        "year": year,
        "annual_leave_days": 0,  # 简化：实际应从规则表读取年假额度
        "sick_leave_days": 0,
        "used_days": approved_days,
    }