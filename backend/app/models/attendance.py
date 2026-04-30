from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Time, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    
    # 考勤时间
    punch_date = Column(Date, nullable=False, comment="考勤日期")
    punch_time = Column(DateTime, nullable=False, comment="考勤时间")
    
    # 考勤类型
    punch_type = Column(String(20), default="check_in", comment="类型: check_in/check_out")
    verify_type = Column(Integer, default=0, comment="验证方式: 0指纹 1面部 2密码 3卡")
    
    # 状态
    status = Column(String(20), default="normal", comment="状态: normal/late/early/exception")
    
    # 原始数据
    raw_data = Column(String(500), nullable=True, comment="原始考勤数据")
    
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    employee = relationship("Employee", back_populates="attendance_records", foreign_keys=[employee_id])
    device = relationship("Device", foreign_keys=[device_id])


class AttendanceSummary(Base):
    __tablename__ = "attendance_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    summary_date = Column(Date, nullable=False, comment="统计日期")
    
    # 出勤统计
    work_days = Column(Integer, default=0, comment="应出勤天数")
    actual_days = Column(Integer, default=0, comment="实际出勤天数")
    late_count = Column(Integer, default=0, comment="迟到次数")
    early_count = Column(Integer, default=0, comment="早退次数")
    absent_count = Column(Integer, default=0, comment="旷工天数")
    
    # 工时统计
    total_work_hours = Column(String(20), nullable=True, comment="总工时")
    overtime_hours = Column(String(20), nullable=True, comment="加班工时")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
