from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Time, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Shift(Base):
    """班次模板"""
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment="班次名称，如：早班/中班/夜班")
    shift_type = Column(String(20), nullable=False, comment="班次类型：day/night/middle/custom")
    check_in_start = Column(Time, nullable=False, comment="上班打卡开始时间")
    check_in_end = Column(Time, nullable=False, comment="上班打卡结束时间")
    check_out_start = Column(Time, nullable=False, comment="下班打卡开始时间")
    check_out_end = Column(Time, nullable=False, comment="下班打卡结束时间")
    work_hours = Column(String(20), nullable=True, comment="标准工作时数")
    color = Column(String(20), nullable=True, comment="前端显示颜色")
    remark = Column(String(200), nullable=True, comment="备注")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    assignments = relationship("ShiftAssignment", back_populates="shift")


class ShiftAssignment(Base):
    """员工班次分配"""
    __tablename__ = "shift_assignments"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    start_date = Column(String(10), nullable=False, comment="生效日期 YYYY-MM-DD")
    end_date = Column(String(10), nullable=True, comment="失效日期 YYYY-MM-DD，null表示长期")
    week_days = Column(String(50), nullable=True, comment="周几生效，如：1,2,3,4,5（工作日）/ 0,6（周末）/ 空表示每天")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    employee = relationship("Employee", back_populates="shift_assignments")
    shift = relationship("Shift", back_populates="assignments")


class ScheduleRecord(Base):
    """排班记录（每天每个员工的班次分配结果）"""
    __tablename__ = "schedule_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    schedule_date = Column(String(10), nullable=False, comment="排班日期 YYYY-MM-DD")
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=True)
    shift_name = Column(String(50), nullable=True, comment="班次名称快照")
    shift_type = Column(String(20), nullable=True, comment="班次类型快照")
    check_in_start = Column(Time, nullable=True, comment="上班开始时间快照")
    check_in_end = Column(Time, nullable=True, comment="上班结束时间快照")
    check_out_start = Column(Time, nullable=True, comment="下班开始时间快照")
    check_out_end = Column(Time, nullable=True, comment="下班结束时间快照")
    status = Column(String(20), default="scheduled", comment="scheduled/confirmed/rest_day/leave")
    remark = Column(String(200), nullable=True, comment="备注")
    auto_generated = Column(Boolean, default=False, comment="是否自动生成")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    employee = relationship("Employee", back_populates="schedule_records")
    shift = relationship("Shift")
