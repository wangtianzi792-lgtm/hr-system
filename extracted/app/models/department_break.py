from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class DepartmentBreak(Base):
    """部门休息时间配置"""
    __tablename__ = "department_breaks"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, unique=True, comment="部门ID")
    break_start = Column(String(10), nullable=False, comment="休息开始时间，如 12:00")
    break_end = Column(String(10), nullable=False, comment="休息结束时间，如 13:00")
    break_minutes = Column(Integer, nullable=False, comment="休息时长（分钟）")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
