from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="部门名称")
    code = Column(String(20), unique=True, nullable=True, comment="部门编码")
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True, comment="上级部门")
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True, comment="部门负责人")
    description = Column(String(500), nullable=True, comment="描述")
    sort_order = Column(Integer, default=0, comment="排序")
    is_active = Column(Integer, default=1, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id", overlaps="manager")
    manager = relationship("Employee", foreign_keys=[manager_id], overlaps="employees")
    parent = relationship("Department", back_populates="children", remote_side=[id])
    children = relationship("Department", back_populates="parent")
