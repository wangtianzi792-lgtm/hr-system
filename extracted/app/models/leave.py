"""请假申请/审批"""
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class LeaveRequest(Base):
    """请假申请"""
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type = Column(String(20), nullable=False, comment="leave_type: 年假/病假/事假/婚假/产假/丧假/其他")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Integer, nullable=False)
    reason = Column(Text, nullable=True)
    attach_url = Column(String(500), nullable=True)
    
    status = Column(String(20), default="pending", comment="pending/approved/rejected/cancelled")
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approve_comment = Column(Text, nullable=True)
    approve_time = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    employee = relationship("Employee", foreign_keys=[employee_id])
    approver = relationship("User", foreign_keys=[approver_id])


class OvertimeRequest(Base):
    """加班申请"""
    __tablename__ = "overtime_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(Date, nullable=False, comment="加班日期")
    start_time = Column(String(10), nullable=False, comment="开始时间 HH:MM")
    end_time = Column(String(10), nullable=False, comment="结束时间 HH:MM")
    hours = Column(String(20), nullable=True, comment="加班时长")
    reason = Column(Text, nullable=True)
    
    status = Column(String(20), default="pending")
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approve_comment = Column(Text, nullable=True)
    approve_time = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    employee = relationship("Employee", foreign_keys=[employee_id])
    approver = relationship("User", foreign_keys=[approver_id])


class AttendanceRule(Base):
    """考勤规则配置"""
    __tablename__ = "attendance_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_key = Column(String(50), unique=True, nullable=False, comment="规则键")
    rule_name = Column(String(100), nullable=False, comment="规则名称")
    rule_value = Column(String(500), nullable=True, comment="规则值(JSON)")
    remark = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())