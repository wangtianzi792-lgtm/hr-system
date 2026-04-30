"""考勤管理 API"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, distinct
from typing import List, Optional
from datetime import date, datetime, timedelta
import logging

from app.core.database import get_db
from app.models.attendance import AttendanceRecord, AttendanceSummary
from app.models.employee import Employee
from app.models.department import Department
from app.models.device import Device
from app.schemas.attendance import (
    AttendanceRecordResponse, AttendanceRecordListResponse,
    AttendanceSummaryResponse, AttendanceReportResponse,
    EmployeeAttendanceReport, AttendanceCollectRequest,
    AttendanceExportRequest
)
from app.services.zk_service import ZKServiceManager

router = APIRouter(prefix="/attendance", tags=["考勤管理"])
logger = logging.getLogger(__name__)


def _attendance_to_response(record: AttendanceRecord) -> dict:
    """将考勤记录转为响应 dict"""
    r = {
        "id": record.id,
        "employee_id": record.employee_id,
        "device_id": record.device_id,
        "punch_date": record.punch_date,
        "punch_time": record.punch_time,
        "punch_type": record.punch_type,
        "verify_type": record.verify_type,
        "status": record.status,
        "raw_data": record.raw_data,
        "created_at": record.created_at,
    }
    if record.employee:
        r["employee_name"] = record.employee.name
    if record.device:
        r["device_name"] = record.device.name
    return r


def _infer_punch_type(records_for_employee_on_day: list, current_record_index: int) -> str:
    """根据同一天的考勤次数推断是上班还是下班"""
    if current_record_index % 2 == 0:
        return "check_in"
    return "check_out"


def _detect_status(punch_time: datetime, expect_hour_morning: int = 9,
                   expect_hour_evening: int = 18) -> str:
    """根据打卡时间判断考勤状态"""
    hour = punch_time.hour
    minute = punch_time.minute
    if hour > expect_hour_morning or (hour == expect_hour_morning and minute > 5):
        return "late"
    if hour < expect_hour_evening - 1:
        return "early"
    return "normal"


# ---- 考勤记录查询 ----

@router.get("/records", response_model=AttendanceRecordListResponse)
def get_attendance_records(
    employee_id: Optional[int] = None,
    department_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取考勤记录列表"""
    query = db.query(AttendanceRecord).join(Employee)

    if employee_id:
        query = query.filter(AttendanceRecord.employee_id == employee_id)
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    if start_date:
        query = query.filter(AttendanceRecord.punch_date >= start_date)
    if end_date:
        query = query.filter(AttendanceRecord.punch_date <= end_date)
    if status:
        query = query.filter(AttendanceRecord.status == status)

    total = query.count()
    records = query.order_by(AttendanceRecord.punch_time.desc()).offset(skip).limit(limit).all()

    return {"total": total, "items": [_attendance_to_response(r) for r in records]}


@router.get("/records/{record_id}", response_model=AttendanceRecordResponse)
def get_attendance_record(record_id: int, db: Session = Depends(get_db)):
    """获取单条考勤记录"""
    record = db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return _attendance_to_response(record)


@router.get("/punch-records")
def get_punch_records(
    skip: int = 0,
    limit: int = 100,
    employee_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """原始打卡记录（供考勤记录页面使用）"""
    from app.models.raw_punch import RawPunchRecord
    from app.models.employee import Employee

    query = db.query(RawPunchRecord)
    if employee_id:
        query = query.filter(RawPunchRecord.employee_id == employee_id)
    if start_date:
        query = query.filter(RawPunchRecord.punch_time >= start_date)
    if end_date:
        query = query.filter(RawPunchRecord.punch_time <= end_date + " 23:59:59")

    total = query.count()
    records = query.order_by(RawPunchRecord.punch_time.desc()).offset(skip).limit(limit).all()

    items = []
    for r in records:
        emp = db.query(Employee).filter(Employee.id == r.employee_id).first() if r.employee_id else None
        items.append({
            "id": r.id,
            "employee_id": r.employee_id,
            "employee_name": emp.name if emp else None,
            "employee_no": emp.employee_no if emp else None,
            "device_id": r.device_id,
            "punch_time": r.punch_time.isoformat() if r.punch_time else None,
            "verify_type": r.verify_type,
            "punch_method": r.punch_method,
            "is_anomaly": r.is_anomaly,
            "anomaly_reason": r.anomaly_reason,
            "is_processed": r.is_processed,
        })
    return {"total": total, "items": items}


# ---- 考勤采集 ----

def _collect_from_device(device: Device, db: Session) -> dict:
    """从单个设备采集考勤记录"""
    collected = 0
    skipped = 0
    errors = []

    try:
        raw_records = ZKServiceManager.sync_attendance(device.ip_address, device.port)
        logger.info(f"从 {device.name}({device.ip_address}) 获取到 {len(raw_records)} 条原始记录")

        # 按 (user_id, timestamp) 分组，只取每组最早一条（去重）
        seen = set()
        deduplicated = []
        for rec in raw_records:
            key = (rec.get("user_id"), str(rec.get("timestamp", "")))
            if key not in seen:
                seen.add(key)
                deduplicated.append(rec)

        for raw in deduplicated:
            try:
                user_id = raw.get("user_id", "")
                if not user_id:
                    skipped += 1
                    continue

                # 查找本地员工（通过工号或 zk_user_id）
                employee = db.query(Employee).filter(
                    or_(
                        Employee.zk_user_id == int(user_id),
                        Employee.employee_no == str(user_id),
                        Employee.id == int(user_id)
                    )
                ).first()

                if not employee:
                    skipped += 1
                    continue

                ts = raw.get("timestamp")
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                elif hasattr(ts, "timetuple"):
                    ts = datetime.fromtimestamp(ts.timestamp())

                punch_date = ts.date()
                punch_time = ts if ts else datetime.now()
                punch_type = "check_in" if raw.get("punch", 0) in [0, 1] else "check_out"
                verify_type = raw.get("status", 0)

                # 检查是否已存在
                exists = db.query(AttendanceRecord).filter(
                    AttendanceRecord.employee_id == employee.id,
                    AttendanceRecord.punch_time == punch_time,
                    AttendanceRecord.device_id == device.id
                ).first()
                if exists:
                    skipped += 1
                    continue

                record = AttendanceRecord(
                    employee_id=employee.id,
                    device_id=device.id,
                    punch_date=punch_date,
                    punch_time=punch_time,
                    punch_type=punch_type,
                    verify_type=verify_type,
                    status="normal",
                    raw_data=str(raw)
                )
                db.add(record)
                collected += 1

            except Exception as e:
                logger.warning(f"处理记录失败: {e}")
                errors.append(str(e))

        db.commit()
        # 更新设备最后同步时间
        device.last_sync = datetime.now()
        db.commit()

        return {"device": device.name, "collected": collected, "skipped": skipped, "errors": errors}

    except Exception as e:
        logger.error(f"采集设备 {device.name} 失败: {e}")
        return {"device": device.name, "collected": 0, "skipped": 0, "errors": [str(e)]}


@router.post("/collect")
def collect_attendance(
    body: Optional[AttendanceCollectRequest] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """手动采集考勤数据（从考勤机同步）"""
    if body and body.device_id:
        device = db.query(Device).filter(Device.id == body.device_id, Device.is_active == True).first()
        if not device:
            raise HTTPException(status_code=404, detail="设备不存在")
        devices_to_collect = [device]
    else:
        devices_to_collect = db.query(Device).filter(Device.is_active == True).all()

    if not devices_to_collect:
        raise HTTPException(status_code=400, detail="没有可采集的设备")

    results = []
    for device in devices_to_collect:
        result = _collect_from_device(device, db)
        results.append(result)

    total_collected = sum(r["collected"] for r in results)

    return {
        "message": f"采集完成，共获取 {total_collected} 条新记录",
        "details": results
    }


# ---- 考勤统计 ----

@router.get("/statistics", response_model=List[AttendanceSummaryResponse])
def get_attendance_statistics(
    start_date: date,
    end_date: date,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取考勤统计（按日）"""
    query = db.query(AttendanceSummary).join(Employee)

    if department_id:
        query = query.filter(Employee.department_id == department_id)
    if start_date:
        query = query.filter(AttendanceSummary.summary_date >= start_date)
    if end_date:
        query = query.filter(AttendanceSummary.summary_date <= end_date)

    summaries = query.order_by(AttendanceSummary.summary_date.desc()).all()

    result = []
    for s in summaries:
        item = {
            "id": s.id,
            "employee_id": s.employee_id,
            "summary_date": s.summary_date,
            "work_days": s.work_days,
            "actual_days": s.actual_days,
            "late_count": s.late_count,
            "early_count": s.early_count,
            "absent_count": s.absent_count,
            "total_work_hours": s.total_work_hours,
            "overtime_hours": s.overtime_hours,
            "created_at": s.created_at,
        }
        if s.employee:
            item["employee_name"] = s.employee.name
        result.append(item)

    return result


@router.get("/report", response_model=AttendanceReportResponse)
def get_attendance_report(
    start_date: date,
    end_date: date,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取考勤报表（按人员汇总）"""
    # 获取统计周期内的员工
    emp_query = db.query(Employee).filter(Employee.is_active == True, Employee.status == "active")
    if department_id:
        emp_query = emp_query.filter(Employee.department_id == department_id)
    employees = emp_query.all()

    # 计算应出勤天数（排除周末）
    delta = (end_date - start_date).days + 1
    work_days_total = sum(1 for i in range(delta)
                          if (start_date + timedelta(i)).weekday() < 5)

    items = []
    for emp in employees:
        # 查询该员工统计周期内的考勤记录
        records = db.query(AttendanceRecord).filter(
            AttendanceRecord.employee_id == emp.id,
            AttendanceRecord.punch_date >= start_date,
            AttendanceRecord.punch_date <= end_date
        ).all()

        # 按日期分组
        records_by_date = {}
        for rec in records:
            d = rec.punch_date
            if d not in records_by_date:
                records_by_date[d] = []
            records_by_date[d].append(rec)

        actual_days = len(records_by_date)
        late_count = sum(1 for recs in records_by_date.values()
                        for r in recs if r.punch_type == "check_in" and r.status == "late")
        early_count = sum(1 for recs in records_by_date.values()
                         for r in recs if r.punch_type == "check_out" and r.status == "early")
        absent_days = max(0, work_days_total - actual_days)
        normal_days = actual_days - late_count - early_count

        # 计算工时（简化：首次check_in到末次check_out）
        total_minutes = 0
        for day_records in records_by_date.values():
            times = sorted([r.punch_time for r in day_records])
            if len(times) >= 2:
                delta_t = (times[-1] - times[0]).total_seconds() / 60
                total_minutes += delta_t
        hours = int(total_minutes // 60)
        mins = int(total_minutes % 60)
        total_work_hours = f"{hours}h{mins}m" if hours else None

        item = EmployeeAttendanceReport(
            employee_id=emp.id,
            employee_name=emp.name,
            department_name=emp.department.name if emp.department else None,
            position=emp.position,
            work_days=work_days_total,
            actual_days=actual_days,
            late_count=late_count,
            early_count=early_count,
            absent_days=absent_days,
            normal_days=max(0, normal_days),
            total_work_hours=total_work_hours,
        )
        items.append(item)

    return {"total": len(items), "items": items}


# ---- 考勤导出 ----

@router.post("/export")
def export_attendance(
    start_date: date,
    end_date: date,
    department_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    format: str = "xlsx",
    db: Session = Depends(get_db)
):
    """导出考勤数据"""
    # 查询考勤记录
    query = db.query(AttendanceRecord).join(Employee)
    if employee_id:
        query = query.filter(AttendanceRecord.employee_id == employee_id)
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    if start_date:
        query = query.filter(AttendanceRecord.punch_date >= start_date)
    if end_date:
        query = query.filter(AttendanceRecord.punch_date <= end_date)

    records = query.order_by(AttendanceRecord.punch_time.asc()).all()

    if format == "csv":
        import csv, io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["工号", "姓名", "部门", "日期", "时间", "类型", "验证方式", "状态"])
        for r in records:
            writer.writerow([
                r.employee.employee_no if r.employee else "",
                r.employee.name if r.employee else "",
                r.employee.department.name if r.employee and r.employee.department else "",
                r.punch_date,
                r.punch_time.strftime("%H:%M:%S"),
                "上班" if r.punch_type == "check_in" else "下班",
                ["指纹", "面部", "密码", "卡", "混合"][r.verify_type] if r.verify_type < 5 else "其他",
                {"normal": "正常", "late": "迟到", "early": "早退", "exception": "异常"}.get(r.status, r.status)
            ])
        return {
            "format": "csv",
            "data": output.getvalue(),
            "count": len(records)
        }

    # xlsx 格式（返回记录数，前端可自行生成或后端集成 xlsxwriter）
    return {
        "format": "xlsx",
        "message": f"共 {len(records)} 条记录待导出，请访问 /api/attendance/export/file",
        "count": len(records),
        "start_date": str(start_date),
        "end_date": str(end_date),
    }


@router.get("/summary/today")
def get_today_summary(db: Session = Depends(get_db)):
    """获取今日考勤概况"""
    today = date.today()
    records = db.query(AttendanceRecord).filter(AttendanceRecord.punch_date == today).all()

    # 按员工分组
    checked_in = set(r.employee_id for r in records if r.punch_type == "check_in")
    checked_out = set(r.employee_id for r in records if r.punch_type == "check_out")
    total_employees = db.query(Employee).filter(Employee.status == "active", Employee.is_active == True).count()
    late_today = sum(1 for r in records if r.punch_type == "check_in" and r.status == "late")

    return {
        "date": today,
        "total_employees": total_employees,
        "checked_in": len(checked_in),
        "checked_out": len(checked_out),
        "not_checked_in": total_employees - len(checked_in),
        "late_count": late_today,
    }
