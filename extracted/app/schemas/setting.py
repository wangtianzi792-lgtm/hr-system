from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SettingBase(BaseModel):
    key: str
    value: Optional[str] = None
    description: Optional[str] = None


class SettingCreate(SettingBase):
    pass


class SettingUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None


class SettingResponse(SettingBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CompanyInfo(BaseModel):
    name: str = ""
    short_name: str = ""
    credit_code: str = ""
    address: str = ""
    phone: str = ""


class AttendanceRule(BaseModel):
    work_start_time: str = "08:30"
    work_end_time: str = "17:30"
    late_tolerance: int = 5
    early_tolerance: int = 5
    work_days: List[str] = ["1", "2", "3", "4", "5"]


class LeaveRule(BaseModel):
    annual_leave_days: int = 5
    sick_leave_days: int = 10
    personal_leave_days: int = 5
    compensatory_leave_days: int = 0


class SystemConfig(BaseModel):
    system_name: str = "海昌新材人事考勤系统"
    session_timeout: str = "120"
    auto_backup: bool = True
    backup_interval: str = "daily"
    theme: str = "light"


class OperationLogCreate(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    detail: Optional[str] = None
    ip_address: Optional[str] = None


class OperationLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    detail: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
