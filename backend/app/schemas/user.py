from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PermissionResponse(BaseModel):
    id: int
    name: str
    category: str
    display_name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    sort_order: int = 0


class RoleCreate(RoleBase):
    permission_ids: List[int] = []


class RoleUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(RoleBase):
    id: int
    is_system: bool
    permissions: List[PermissionResponse] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    role_id: int