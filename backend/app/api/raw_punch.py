"""原始打卡记录查询 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc, func
from typing import List, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.raw_punch import RawPunchRecord
from app.models.employee import Employee
from app.models.device import Device
from app.models.user import User
from app.schemas.raw_punch import (
    RawPunchResponse, RawPunchListResponse,
    RawPunchMarkAnomalyRequest, RawPunchLinkRequest
)

router = APIRouter(prefix="/raw-punch", tags=["原始打卡记录"])


def _record_to_response(record: RawPunchRecord) -> dict:
    result = {
        "id": record.id,
        "employee_id": record.employee_id,
        "device_id": record.device_id,
        "punch_time": record.punch_time,
        "verify_type": record.verify_type,
        "punch_method": record.punch_method,
        "is_processed": record.is_processed,
        "is_anomaly": record.is_anomaly,
        "anomaly_reason": record.anomaly_reason,
        "raw_data": record.raw_data,
        "created_at": record.created_at,
    }
    if record.employee:
        result["employee_name"] = record.employee.name
        result["employee_no"] = record.employee.employee_no
    if record.device:
        result["device_name"] = record.device.name
    return result


@router.get("", response_model=RawPunchListResponse)
def list_raw_punch_records(
    employee_id: Optional[int] = None,
    device_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    is_anomaly: Optional[bool] = None,
    is_processed: Optional[bool] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查询原始打卡记录"""
    query = db.query(RawPunchRecord).options(
        joinedload(RawPunchRecord.employee),
        joinedload(RawPunchRecord.device)
    )

    if employee_id:
        query = query.filter(RawPunchRecord.employee_id == employee_id)
    if device_id:
        query = query.filter(RawPunchRecord.device_id == device_id)
    if start_date:
        query = query.filter(RawPunchRecord.punch_time >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(RawPunchRecord.punch_time <= datetime.combine(end_date, datetime.max.time()))
    if is_anomaly is not None:
        query = query.filter(RawPunchRecord.is_anomaly == is_anomaly)
    if is_processed is not None:
        query = query.filter(RawPunchRecord.is_processed == is_processed)

    total = query.count()
    records = query.order_by(desc(RawPunchRecord.punch_time)).offset(skip).limit(limit).all()

    return {"total": total, "items": [_record_to_response(r) for r in records]}


@router.get("/{record_id}", response_model=RawPunchResponse)
def get_raw_punch_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单条原始打卡记录"""
    record = db.query(RawPunchRecord).options(
        joinedload(RawPunchRecord.employee),
        joinedload(RawPunchRecord.device)
    ).filter(RawPunchRecord.id == record_id).first()

    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return _record_to_response(record)


@router.post("/mark-anomaly")
def mark_anomaly_records(
    data: RawPunchMarkAnomalyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量标记/取消标记异常"""
    records = db.query(RawPunchRecord).filter(RawPunchRecord.id.in_(data.record_ids)).all()
    if not records:
        raise HTTPException(status_code=404, detail="没有找到对应记录")

    for record in records:
        record.is_anomaly = data.is_anomaly
        record.anomaly_reason = data.anomaly_reason

    db.commit()
    return {"message": f"已更新 {len(records)} 条记录", "count": len(records)}


@router.post("/link-employee")
def link_employee(
    data: RawPunchLinkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量关联员工"""
    employee = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="员工不存在")

    records = db.query(RawPunchRecord).filter(RawPunchRecord.id.in_(data.record_ids)).all()
    if not records:
        raise HTTPException(status_code=404, detail="没有找到对应记录")

    for record in records:
        record.employee_id = data.employee_id

    db.commit()
    return {"message": f"已关联 {len(records)} 条记录到员工 {employee.name}", "count": len(records)}


@router.get("/statistics/anomaly")
def get_anomaly_statistics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    device_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """异常打卡统计"""
    query = db.query(RawPunchRecord).filter(RawPunchRecord.is_anomaly == True)

    if start_date:
        query = query.filter(RawPunchRecord.punch_time >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(RawPunchRecord.punch_time <= datetime.combine(end_date, datetime.max.time()))
    if device_id:
        query = query.filter(RawPunchRecord.device_id == device_id)

    total = query.count()

    # 按设备分组
    by_device = db.query(
        RawPunchRecord.device_id,
        func.count(RawPunchRecord.id).label("count")
    ).filter(RawPunchRecord.is_anomaly == True)
    if start_date:
        by_device = by_device.filter(RawPunchRecord.punch_time >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        by_device = by_device.filter(RawPunchRecord.punch_time <= datetime.combine(end_date, datetime.max.time()))
    if device_id:
        by_device = by_device.filter(RawPunchRecord.device_id == device_id)
    by_device = by_device.group_by(RawPunchRecord.device_id).all()

    # 按原因分组
    anomaly_reasons = db.query(
        RawPunchRecord.anomaly_reason,
        func.count(RawPunchRecord.id).label("count")
    ).filter(
        RawPunchRecord.is_anomaly == True,
        RawPunchRecord.anomaly_reason.isnot(None)
    )
    if start_date:
        anomaly_reasons = anomaly_reasons.filter(RawPunchRecord.punch_time >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        anomaly_reasons = anomaly_reasons.filter(RawPunchRecord.punch_time <= datetime.combine(end_date, datetime.max.time()))
    if device_id:
        anomaly_reasons = anomaly_reasons.filter(RawPunchRecord.device_id == device_id)
    anomaly_reasons = anomaly_reasons.group_by(RawPunchRecord.anomaly_reason).all()

    return {
        "total_anomaly": total,
        "by_device": [{"device_id": d[0], "count": d[1]} for d in by_device],
        "by_reason": [{"reason": r[0], "count": r[1]} for r in anomaly_reasons],
    }
