"""部门相关 Pydantic 模型"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class DepartmentBase(BaseModel):
    name: str
    code: Optional[str] = None
    parent_id: Optional[int] = None
    manager_id: Optional[int] = None
    description: Optional[str] = None
    sort_order: int = 0
    is_active: int = 1


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    parent_id: Optional[int] = None
    manager_id: Optional[int] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[int] = None


class DepartmentResponse(DepartmentBase):
    id: int
    parent_name: Optional[str] = None
    manager_name: Optional[str] = None
    employee_count: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DepartmentTreeResponse(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int = 0
    is_active: int = 1
    children: List["DepartmentTreeResponse"] = []

    class Config:
        from_attributes = True


# 允许前向引用
DepartmentTreeResponse.model_rebuild()
