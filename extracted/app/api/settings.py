from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import json

from app.core.database import get_db
from app.models.setting import SystemSetting, OperationLog
from app.schemas.setting import (
    CompanyInfo, AttendanceRule, LeaveRule, SystemConfig,
    OperationLogCreate, OperationLogResponse
)

router = APIRouter(prefix="/settings", tags=["settings"])


# ========== 辅助函数 ==========

def get_setting_value(db: Session, key: str, default: str = "") -> str:
    """获取单个设置值"""
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    return setting.value if setting else default


def set_setting_value(db: Session, key: str, value: str, description: str = ""):
    """设置单个设置值"""
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if setting:
        setting.value = value
    else:
        setting = SystemSetting(key=key, value=value, description=description)
        db.add(setting)
    db.commit()


def add_operation_log(db: Session, user_id: Optional[int], username: Optional[str],
                      action: str, detail: str, ip_address: Optional[str]):
    """添加操作日志"""
    log = OperationLog(
        user_id=user_id,
        username=username,
        action=action,
        detail=detail,
        ip_address=ip_address
    )
    db.add(log)
    db.commit()


# ========== 公司信息 ==========

@router.get("/company", response_model=CompanyInfo)
def get_company_info(db: Session = Depends(get_db)):
    return CompanyInfo(
        name=get_setting_value(db, "company_name", "海昌新材"),
        short_name=get_setting_value(db, "company_short_name", "海昌新材"),
        credit_code=get_setting_value(db, "company_credit_code", ""),
        address=get_setting_value(db, "company_address", ""),
        phone=get_setting_value(db, "company_phone", "")
    )


@router.post("/company")
def save_company_info(data: CompanyInfo, request: Request, db: Session = Depends(get_db)):
    set_setting_value(db, "company_name", data.name, "公司名称")
    set_setting_value(db, "company_short_name", data.short_name, "公司简称")
    set_setting_value(db, "company_credit_code", data.credit_code, "统一社会信用代码")
    set_setting_value(db, "company_address", data.address, "公司地址")
    set_setting_value(db, "company_phone", data.phone, "联系电话")
    add_operation_log(db, None, "管理员", "修改", f"更新公司信息: {data.name}",
                      request.client.host if request.client else None)
    return {"message": "公司信息保存成功"}


# ========== 考勤规则 ==========

@router.get("/attendance-rule", response_model=AttendanceRule)
def get_attendance_rule(db: Session = Depends(get_db)):
    work_days_str = get_setting_value(db, "attendance_work_days", '["1","2","3","4","5"]')
    try:
        work_days = json.loads(work_days_str)
    except:
        work_days = ["1", "2", "3", "4", "5"]
    return AttendanceRule(
        work_start_time=get_setting_value(db, "attendance_work_start_time", "08:30"),
        work_end_time=get_setting_value(db, "attendance_work_end_time", "17:30"),
        late_tolerance=int(get_setting_value(db, "attendance_late_tolerance", "5")),
        early_tolerance=int(get_setting_value(db, "attendance_early_tolerance", "5")),
        work_days=work_days
    )


@router.post("/attendance-rule")
def save_attendance_rule(data: AttendanceRule, request: Request, db: Session = Depends(get_db)):
    set_setting_value(db, "attendance_work_start_time", data.work_start_time, "上班时间")
    set_setting_value(db, "attendance_work_end_time", data.work_end_time, "下班时间")
    set_setting_value(db, "attendance_late_tolerance", str(data.late_tolerance), "迟到容忍")
    set_setting_value(db, "attendance_early_tolerance", str(data.early_tolerance), "早退容忍")
    set_setting_value(db, "attendance_work_days", json.dumps(data.work_days), "工作日")
    add_operation_log(db, None, "管理员", "修改", "更新考勤规则", request.client.host if request.client else None)
    return {"message": "考勤规则保存成功"}


# ========== 假期设置 ==========

@router.get("/leave-rule", response_model=LeaveRule)
def get_leave_rule(db: Session = Depends(get_db)):
    return LeaveRule(
        annual_leave_days=int(get_setting_value(db, "leave_annual_days", "5")),
        sick_leave_days=int(get_setting_value(db, "leave_sick_days", "10")),
        personal_leave_days=int(get_setting_value(db, "leave_personal_days", "5")),
        compensatory_leave_days=int(get_setting_value(db, "leave_compensatory_days", "0"))
    )


@router.post("/leave-rule")
def save_leave_rule(data: LeaveRule, request: Request, db: Session = Depends(get_db)):
    set_setting_value(db, "leave_annual_days", str(data.annual_leave_days), "年假天数")
    set_setting_value(db, "leave_sick_days", str(data.sick_leave_days), "病假天数")
    set_setting_value(db, "leave_personal_days", str(data.personal_leave_days), "事假天数")
    set_setting_value(db, "leave_compensatory_days", str(data.compensatory_leave_days), "调休天数")
    add_operation_log(db, None, "管理员", "修改", "更新假期设置", request.client.host if request.client else None)
    return {"message": "假期设置保存成功"}


# ========== 系统设置 ==========

@router.get("/system", response_model=SystemConfig)
def get_system_config(db: Session = Depends(get_db)):
    return SystemConfig(
        system_name=get_setting_value(db, "system_name", "海昌新材人事考勤系统"),
        session_timeout=get_setting_value(db, "system_session_timeout", "120"),
        auto_backup=get_setting_value(db, "system_auto_backup", "true").lower() == "true",
        backup_interval=get_setting_value(db, "system_backup_interval", "daily"),
        theme=get_setting_value(db, "system_theme", "light")
    )


@router.post("/system")
def save_system_config(data: SystemConfig, request: Request, db: Session = Depends(get_db)):
    set_setting_value(db, "system_name", data.system_name, "系统名称")
    set_setting_value(db, "system_session_timeout", data.session_timeout, "登录有效期")
    set_setting_value(db, "system_auto_backup", "true" if data.auto_backup else "false", "自动备份")
    set_setting_value(db, "system_backup_interval", data.backup_interval, "备份周期")
    set_setting_value(db, "system_theme", data.theme, "系统主题")
    add_operation_log(db, None, "管理员", "修改", "更新系统设置", request.client.host if request.client else None)
    return {"message": "系统设置保存成功"}


# ========== 操作日志 ==========

@router.get("/logs", response_model=dict)
def get_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    action: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(OperationLog)
    if action:
        query = query.filter(OperationLog.action == action)

    total = query.count()
    logs = query.order_by(OperationLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "items": [OperationLogResponse.model_validate(log) for log in logs]
    }


@router.post("/logs")
def create_log(data: OperationLogCreate, db: Session = Depends(get_db)):
    log = OperationLog(**data.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return OperationLogResponse.model_validate(log)
