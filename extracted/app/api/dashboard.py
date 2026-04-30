"""Dashboard API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import date, timedelta

from app.core.database import get_db
from app.models.employee import Employee
from app.models.department import Department
from app.models.attendance import AttendanceRecord
from app.models.leave import LeaveRequest

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

STATUS_MAP = {
    "normal": ("正常", "success"),
    "late": ("迟到", "warning"),
    "early": ("早退", "info"),
    "absent": ("缺勤", "danger"),
}


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    today = date.today()
    total = db.query(Employee).filter(Employee.is_active == True).count()
    punched = db.query(func.count(distinct(AttendanceRecord.employee_id))).filter(
        AttendanceRecord.punch_date == today
    ).scalar() or 0
    late = db.query(func.count(distinct(AttendanceRecord.employee_id))).filter(
        AttendanceRecord.punch_date == today,
        AttendanceRecord.status == "late"
    ).scalar() or 0
    absent = total - punched
    pending = db.query(LeaveRequest).filter(LeaveRequest.status == "pending").count()
    return {
        "total_employees": total,
        "today_punched": punched,
        "today_late": late,
        "today_absent": absent,
        "pending_leaves": pending,
        "attendance_rate": round(punched / total * 100, 1) if total > 0 else 0
    }


@router.get("/today")
def get_today_stats(db: Session = Depends(get_db)):
    today = date.today()
    rows = db.query(
        AttendanceRecord.status,
        func.count(distinct(AttendanceRecord.employee_id))
    ).filter(AttendanceRecord.punch_date == today).group_by(AttendanceRecord.status).all()
    result = {"normal": 0, "late": 0, "early": 0, "absent": 0}
    for status, count in rows:
        if status in result:
            result[status] = count
    return result


@router.get("/week-trend")
def get_week_trend(db: Session = Depends(get_db)):
    today = date.today()
    dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    result = []
    for d in dates:
        count = db.query(func.count(distinct(AttendanceRecord.employee_id))).filter(
            AttendanceRecord.punch_date == d
        ).scalar() or 0
        result.append({"date": d.strftime("%m-%d"), "count": count})
    return result


@router.get("/dept-stats")
def get_dept_stats(db: Session = Depends(get_db)):
    today = date.today()
    depts = db.query(Department).all()
    result = []
    for dept in depts:
        total = db.query(Employee).filter(
            Employee.department_id == dept.id, Employee.is_active == True
        ).count()
        punched = db.query(func.count(distinct(AttendanceRecord.employee_id))).join(
            Employee, Employee.id == AttendanceRecord.employee_id
        ).filter(
            Employee.department_id == dept.id, AttendanceRecord.punch_date == today
        ).scalar() or 0
        result.append({
            "dept_name": dept.name,
            "total": total,
            "punched": punched,
            "rate": round(punched / total * 100, 1) if total > 0 else 0
        })
    return result


@router.get("/recent-records")
def get_recent_records(limit: int = 10, db: Session = Depends(get_db)):
    records = db.query(AttendanceRecord).join(Employee).order_by(
        AttendanceRecord.punch_time.desc()
    ).limit(limit).all()
    result = []
    for r in records:
        text, tag = STATUS_MAP.get(r.status, ("未知", "info"))
        result.append({
            "id": r.id,
            "employee_name": r.employee.name if r.employee else "-",
            "department": r.employee.department.name if r.employee and r.employee.department else "-",
            "punch_time": r.punch_time.strftime("%Y-%m-%d %H:%M:%S") if r.punch_time else "-",
            "status": r.status,
            "status_text": text,
            "tag_type": tag
        })
    return result
