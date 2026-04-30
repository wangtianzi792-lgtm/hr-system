from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3
from datetime import datetime, date

router = APIRouter(prefix="/work-hours", tags=["工时管理"])

def get_conn():
    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row
    return conn

# ==================== 班次配置 ====================

class ShiftConfig(BaseModel):
    name: str
    start_time: str  # "08:00"
    end_time: str    # "17:00"
    break_duration: int = 60  # 分钟
    is_night_shift: bool = False
    overtime_threshold: int = 0  # 超过多少分钟算加班

@router.get("/shifts")
def list_shifts():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shift_configs ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return {"items": [dict(r) for r in rows]}

@router.post("/shifts")
def create_shift(data: ShiftConfig):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO shift_configs (name, start_time, end_time, break_duration, is_night_shift, overtime_threshold)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (data.name, data.start_time, data.end_time, data.break_duration, data.is_night_shift, data.overtime_threshold))
    conn.commit()
    conn.close()
    return {"id": cursor.lastrowid}

@router.put("/shifts/{shift_id}")
def update_shift(shift_id: int, data: ShiftConfig):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""UPDATE shift_configs SET name=?, start_time=?, end_time=?, break_duration=?, is_night_shift=?, overtime_threshold=? WHERE id=?""",
        (data.name, data.start_time, data.end_time, data.break_duration, data.is_night_shift, data.overtime_threshold, shift_id))
    conn.commit()
    conn.close()
    return {"message": "更新成功"}

@router.delete("/shifts/{shift_id}")
def delete_shift(shift_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM shift_configs WHERE id=?", (shift_id,))
    conn.commit()
    conn.close()
    return {"message": "删除成功"}

# ==================== 员工排班绑定 ====================

class EmployeeShift(BaseModel):
    employee_no: str
    shift_id: int
    effective_month: str  # "2025-05"

@router.get("/employee-shifts")
def list_employee_shifts(month: Optional[str] = None):
    conn = get_conn()
    cursor = conn.cursor()
    if month:
        cursor.execute("""SELECT es.*, sc.name as shift_name, sc.start_time, sc.end_time, r.姓名, r.岗位
            FROM employee_shifts es
            JOIN shift_configs sc ON es.shift_id = sc.id
            JOIN roster r ON es.employee_no = r.工号
            WHERE es.effective_month=? ORDER BY es.id DESC""", (month,))
    else:
        cursor.execute("""SELECT es.*, sc.name as shift_name, sc.start_time, sc.end_time, r.姓名, r.岗位
            FROM employee_shifts es
            JOIN shift_configs sc ON es.shift_id = sc.id
            JOIN roster r ON es.employee_no = r.工号
            ORDER BY es.id DESC""")
    rows = cursor.fetchall()
    conn.close()
    return {"items": [dict(r) for r in rows]}

@router.post("/employee-shifts")
def create_employee_shift(data: EmployeeShift):
    conn = get_conn()
    cursor = conn.cursor()
    # 检查该员工该月份是否已有排班，有则覆盖
    cursor.execute("SELECT id FROM employee_shifts WHERE employee_no=? AND effective_month=?", (data.employee_no, data.effective_month))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("""UPDATE employee_shifts SET shift_id=? WHERE employee_no=? AND effective_month=?""",
            (data.shift_id, data.employee_no, data.effective_month))
        conn.commit()
        conn.close()
        return {"message": "排班已更新", "id": existing["id"]}
    cursor.execute("""INSERT INTO employee_shifts (employee_no, shift_id, effective_month) VALUES (?, ?, ?)""",
        (data.employee_no, data.shift_id, data.effective_month))
    conn.commit()
    conn.close()
    return {"id": cursor.lastrowid}

@router.delete("/employee-shifts/{id}")
def delete_employee_shift(id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employee_shifts WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return {"message": "删除成功"}

# ==================== 请假单 ====================

class LeaveRequest(BaseModel):
    employee_no: str
    leave_type: str  # 年假/病假/事假/婚假/产假/其他
    start_date: str  # "2025-05-01"
    end_date: str
    hours: float  # 每天工时，默认8
    reason: Optional[str] = ""
    approver: Optional[str] = ""
    status: str = "pending"

@router.get("/leaves")
def list_leaves(month: Optional[str] = None, employee_no: Optional[str] = None):
    conn = get_conn()
    cursor = conn.cursor()
    sql = """SELECT lr.*, r.姓名, r.岗位 FROM leave_requests lr JOIN roster r ON lr.employee_no=r.工号 WHERE 1=1"""
    params = []
    if month:
        sql += " AND lr.start_date LIKE ?"
        params.append(f"{month}%")
    if employee_no:
        sql += " AND lr.employee_no=?"
        params.append(employee_no)
    sql += " ORDER BY lr.start_date DESC"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return {"items": [dict(r) for r in rows]}

@router.post("/leaves")
def create_leave(data: LeaveRequest):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO leave_requests (employee_no, leave_type, start_date, end_date, hours, reason, approver, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (data.employee_no, data.leave_type, data.start_date, data.end_date, data.hours, data.reason, data.approver, data.status))
    conn.commit()
    conn.close()
    return {"id": cursor.lastrowid}

@router.put("/leaves/{id}/approve")
def approve_leave(id: int, approver: str = ""):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE leave_requests SET status='approved', approver=? WHERE id=?", (approver, id))
    conn.commit()
    conn.close()
    return {"message": "请假审批完成"}

# ==================== 加班申请 ====================

class OvertimeRequest(BaseModel):
    employee_no: str
    date: str
    hours: float
    reason: Optional[str] = ""
    approver: Optional[str] = ""
    status: str = "pending"

@router.get("/overtime")
def list_overtime(month: Optional[str] = None, employee_no: Optional[str] = None):
    conn = get_conn()
    cursor = conn.cursor()
    sql = """SELECT ot.*, r.姓名, r.岗位 FROM overtime_requests ot JOIN roster r ON ot.employee_no=r.工号 WHERE 1=1"""
    params = []
    if month:
        sql += " AND ot.date LIKE ?"
        params.append(f"{month}%")
    if employee_no:
        sql += " AND ot.employee_no=?"
        params.append(employee_no)
    sql += " ORDER BY ot.date DESC"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return {"items": [dict(r) for r in rows]}

@router.post("/overtime")
def create_overtime(data: OvertimeRequest):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO overtime_requests (employee_no, date, hours, reason, approver, status)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (data.employee_no, data.date, data.hours, data.reason, data.approver, data.status))
    conn.commit()
    conn.close()
    return {"id": cursor.lastrowid}

@router.put("/overtime/{id}/approve")
def approve_overtime(id: int, approver: str = ""):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE overtime_requests SET status='approved', approver=? WHERE id=?", (approver, id))
    conn.commit()
    conn.close()
    return {"message": "加班审批完成"}

# ==================== 调休申请 ====================

class AdjustmentRequest(BaseModel):
    employee_no: str
    original_date: str
    original_time: Optional[str] = ""
    new_date: str
    new_time: Optional[str] = ""
    reason: Optional[str] = ""
    approver: Optional[str] = ""
    status: str = "pending"

@router.get("/adjustments")
def list_adjustments(month: Optional[str] = None, employee_no: Optional[str] = None):
    conn = get_conn()
    cursor = conn.cursor()
    sql = """SELECT sa.*, r.姓名, r.岗位 FROM shift_adjustments sa JOIN roster r ON sa.employee_no=r.工号 WHERE 1=1"""
    params = []
    if month:
        sql += " AND sa.original_date LIKE ?"
        params.append(f"{month}%")
    if employee_no:
        sql += " AND sa.employee_no=?"
        params.append(employee_no)
    sql += " ORDER BY sa.original_date DESC"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return {"items": [dict(r) for r in rows]}

@router.post("/adjustments")
def create_adjustment(data: AdjustmentRequest):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO shift_adjustments (employee_no, original_date, original_time, new_date, new_time, reason, approver, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (data.employee_no, data.original_date, data.original_time, data.new_date, data.new_time, data.reason, data.approver, data.status))
    conn.commit()
    conn.close()
    return {"id": cursor.lastrowid}

@router.put("/adjustments/{id}/approve")
def approve_adjustment(id: int, approver: str = ""):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE shift_adjustments SET status='approved', approver=? WHERE id=?", (approver, id))
    conn.commit()
    conn.close()
    return {"message": "调休审批完成"}

# ==================== 工时报表 ====================

@router.get("/daily-report")
def daily_report(month: str, employee_no: Optional[str] = None):
    """某月每日工时报表"""
    conn = get_conn()
    cursor = conn.cursor()

    # 获取该月所有日期
    year, mon = month.split("-")
    from calendar import monthrange
    _, days_in_month = monthrange(int(year), int(mon))

    # 基础 SQL：花名册 + 员工类型
    base_sql = """SELECT r.工号, r.姓名, r.员工类型 FROM roster r WHERE r.是否在职=1"""
    params = []
    if employee_no:
        base_sql += " AND r.工号=?"
        params.append(employee_no)
    base_sql += " ORDER BY r.工号"

    cursor.execute(base_sql, params)
    employees = cursor.fetchall()

    result = []
    for emp in employees:
        emp_no = emp["工号"]
        emp_name = emp["姓名"]
        emp_type = emp["员工类型"]
        is_formal = emp_type == "正式工"

        emp_days = []
        total_regular = 0
        total_overtime = 0
        total_leave = 0

        for day in range(1, days_in_month + 1):
            day_str = f"{year}-{mon:02d}-{day:02d}"
            weekday = datetime.strptime(day_str, "%Y-%m-%d").weekday()
            is_weekend = weekday >= 5  # 周六周日

            # 打卡记录
            cursor.execute("""SELECT check_in, check_out FROM attendance_records
                WHERE employee_no=? AND date=?""", (emp_no, day_str))
            punch = cursor.fetchone()

            # 请假（已审批）
            cursor.execute("""SELECT hours, leave_type FROM leave_requests
                WHERE employee_no=? AND status='approved' AND ? BETWEEN start_date AND end_date""",
                (emp_no, day_str))
            leave = cursor.fetchone()

            # 加班（已审批）
            cursor.execute("""SELECT hours FROM overtime_requests
                WHERE employee_no=? AND status='approved' AND date=? AND employee_no=?""",
                (emp_no, day_str, emp_no))
            overtime = cursor.fetchone()

            # 排班
            cursor.execute("""SELECT sc.name, sc.start_time, sc.end_time, sc.break_duration
                FROM employee_shifts es
                JOIN shift_configs sc ON es.shift_id = sc.id
                WHERE es.employee_no=? AND es.effective_month=? LIMIT 1""",
                (emp_no, month))
            shift = cursor.fetchone()

            if not shift:
                # 无排班按默认标准工时8小时
                standard_hours = 8
                shift_name = "默认班次"
            else:
                shift_name = shift["name"]
                h1, m1 = map(int, shift["start_time"].split(":"))
                h2, m2 = map(int, shift["end_time"].split(":"))
                work_minutes = (h2 * 60 + m2) - (h1 * 60 + m1) - shift["break_duration"]
                standard_hours = work_minutes / 60

            # 计算工时
            if leave:
                day_regular = 0
                day_overtime = 0
                day_leave = leave["hours"]
            elif punch and punch["check_in"] and punch["check_out"]:
                check_in = datetime.strptime(punch["check_in"], "%H:%M")
                check_out = datetime.strptime(punch["check_out"], "%H:%M")
                actual_minutes = (check_out - check_in).seconds / 60 - shift["break_duration"]
                actual_hours = actual_minutes / 60

                if is_formal and overtime:
                    # 正式工：标准工时 + 加班工时
                    day_regular = min(standard_hours, actual_hours)
                    day_overtime = overtime["hours"]
                elif is_formal and actual_hours > standard_hours and not is_weekend:
                    # 正式工超标准算加班
                    day_regular = standard_hours
                    day_overtime = round(actual_hours - standard_hours, 1)
                elif is_weekend and is_formal and actual_hours > 0:
                    # 周末加班（正式工）
                    day_regular = 0
                    day_overtime = actual_hours
                else:
                    day_regular = actual_hours
                    day_overtime = 0
                day_leave = 0
            else:
                day_regular = 0
                day_overtime = 0
                day_leave = 0

            emp_days.append({
                "date": day_str,
                "weekday": ["周一","周二","周三","周四","周五","周六","周日"][weekday],
                "shift": shift_name,
                "regular_hours": day_regular,
                "overtime_hours": day_overtime,
                "leave_hours": day_leave,
                "total": round(day_regular + day_overtime, 1),
                "status": "请假" if day_leave > 0 else ("加班" if day_overtime > 0 else "正常")
            })
            total_regular += day_regular
            total_overtime += day_overtime
            total_leave += day_leave

        result.append({
            "employee_no": emp_no,
            "name": emp_name,
            "employee_type": emp_type,
            "days": emp_days,
            "summary": {
                "regular_hours": round(total_regular, 1),
                "overtime_hours": round(total_overtime, 1),
                "leave_hours": round(total_leave, 1),
                "total_hours": round(total_regular + total_overtime, 1)
            }
        })

    conn.close()
    return {"month": month, "employees": result}

# ==================== 打卡记录接收 ====================

class PunchRecord(BaseModel):
    employee_no: str
    date: str
    check_in: Optional[str] = None
    check_out: Optional[str] = None

@router.post("/punch")
def receive_punch(data: PunchRecord):
    """接收考勤机推送的打卡记录"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""INSERT OR REPLACE INTO attendance_records (employee_no, date, check_in, check_out, updated_at)
        VALUES (?, ?, ?, ?, ?)""",
        (data.employee_no, data.date, data.check_in, data.check_out, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return {"message": "打卡记录已接收"}
