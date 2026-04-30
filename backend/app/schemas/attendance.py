"""考勤相关 Pydantic 模型"""
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List


# ---------- 考勤记录 ----------

class AttendanceRecordBase(BaseModel):
    employee_id: int
    device_id: Optional[int] = None
    punch_date: date
    punch_time: datetime
    punch_type: str = "check_in"  # check_in / check_out
    verify_type: int = 0  # 0指纹 1面部 2密码 3卡 4混合
    status: str = "normal"  # normal / late / early / exception
    raw_data: Optional[str] = None


class AttendanceRecordCreate(AttendanceRecordBase):
    pass


class AttendanceRecordResponse(AttendanceRecordBase):
    id: int
    employee_name: Optional[str] = None
    device_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AttendanceRecordListResponse(BaseModel):
    total: int
    items: List[AttendanceRecordResponse]


# ---------- 考勤统计 ----------

class AttendanceSummaryResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: Optional[str] = None
    summary_date: date
    work_days: int = 0
    actual_days: int = 0
    late_count: int = 0
    early_count: int = 0
    absent_count: int = 0
    total_work_hours: Optional[str] = None
    overtime_hours: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------- 考勤报表（按人员汇总） ----------

class EmployeeAttendanceReport(BaseModel):
    employee_id: int
    employee_name: str
    department_name: Optional[str] = None
    position: Optional[str] = None
    work_days: int = 0
    actual_days: int = 0
    late_count: int = 0
    early_count: int = 0
    absent_days: int = 0
    normal_days: int = 0
    total_work_hours: Optional[str] = None
    overtime_hours: Optional[str] = None


class AttendanceReportResponse(BaseModel):
    total: int
    items: List[EmployeeAttendanceReport]


# ---------- 请求参数 ----------

class AttendanceCollectRequest(BaseModel):
    device_id: Optional[int] = None  # 指定设备，不传则采集所有


class AttendanceExportRequest(BaseModel):
    start_date: date
    end_date: date
    department_id: Optional[int] = None
    employee_id: Optional[int] = None
    format: str = "xlsx"  # xlsx / csv
