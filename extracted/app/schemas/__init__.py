from app.schemas.auth import LoginRequest, LoginResponse, UserInfoResponse, ChangePasswordRequest
from app.schemas.device import DeviceBase, DeviceCreate, DeviceUpdate, DeviceResponse, DeviceStatus
from app.schemas.employee import EmployeeBase, EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse
from app.schemas.department import DepartmentBase, DepartmentCreate, DepartmentUpdate, DepartmentResponse, DepartmentTreeResponse
from app.schemas.attendance import (
    AttendanceRecordResponse, AttendanceRecordListResponse,
    AttendanceSummaryResponse, AttendanceReportResponse,
    EmployeeAttendanceReport, AttendanceCollectRequest, AttendanceExportRequest
)
