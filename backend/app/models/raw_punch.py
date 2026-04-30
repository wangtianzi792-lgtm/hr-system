from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class RawPunchRecord(Base):
    """原始打卡记录（直接从设备采集，未处理）"""
    __tablename__ = "raw_punch_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)

    # 打卡信息
    punch_time = Column(DateTime, nullable=False, comment="打卡时间")
    verify_type = Column(Integer, default=0, comment="验证方式: 0指纹 1面部 2密码 3卡")
    punch_method = Column(Integer, default=0, comment="打卡方式: 0刷卡 1按钮 2脸部")

    # 关联的考勤记录
    attendance_record_id = Column(Integer, ForeignKey("attendance_records.id"), nullable=True)
    is_processed = Column(Boolean, default=False, comment="是否已处理为考勤记录")

    # 异常标记
    is_anomaly = Column(Boolean, default=False, comment="是否异常")
    anomaly_reason = Column(String(100), nullable=True, comment="异常原因")

    # 原始数据
    raw_data = Column(Text, nullable=True, comment="原始数据JSON")

    created_at = Column(DateTime, server_default=func.now())

    # 关联
    employee = relationship("Employee", foreign_keys=[employee_id])
    device = relationship("Device", foreign_keys=[device_id])
    attendance_record = relationship("AttendanceRecord")
