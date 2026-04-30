from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.role import Role
from app.models.permission import Permission, RolePermission
from app.models.user import User
from app.schemas.user import RoleCreate, RoleUpdate, RoleResponse, PermissionResponse

router = APIRouter(prefix="/roles", tags=["角色管理"])


def check_admin(current_user: User):
    """检查是否有管理员权限"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="需要管理员权限")


@router.get("", response_model=List[RoleResponse])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取角色列表"""
    check_admin(current_user)
    roles = db.query(Role).order_by(Role.sort_order).all()
    return roles


@router.post("", response_model=RoleResponse)
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建角色"""
    check_admin(current_user)

    existing = db.query(Role).filter(Role.name == role_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="角色名已存在")

    role = Role(
        name=role_data.name,
        display_name=role_data.display_name,
        description=role_data.description,
        sort_order=role_data.sort_order,
    )
    db.add(role)
    db.flush()

    if role_data.permission_ids:
        for pid in role_data.permission_ids:
            rp = RolePermission(role_id=role.id, permission_id=pid)
            db.add(rp)

    db.commit()
    db.refresh(role)
    return role


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新角色"""
    check_admin(current_user)

    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if role.is_system:
        raise HTTPException(status_code=400, detail="系统内置角色不可修改")

    if role_data.display_name is not None:
        role.display_name = role_data.display_name
    if role_data.description is not None:
        role.description = role_data.description
    if role_data.sort_order is not None:
        role.sort_order = role_data.sort_order
    if role_data.permission_ids is not None:
        db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
        for pid in role_data.permission_ids:
            rp = RolePermission(role_id=role_id, permission_id=pid)
            db.add(rp)

    db.commit()
    db.refresh(role)
    return role


@router.delete("/{role_id}")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除角色"""
    check_admin(current_user)

    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if role.is_system:
        raise HTTPException(status_code=400, detail="系统内置角色不可删除")

    db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
    db.delete(role)
    db.commit()
    return {"message": "删除成功"}


@router.get("/permissions", response_model=List[PermissionResponse])
def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有权限列表"""
    check_admin(current_user)
    return db.query(Permission).order_by(Permission.category).all()


@router.get("/{role_id}/permissions", response_model=List[PermissionResponse])
def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取角色的权限列表"""
    check_admin(current_user)

    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    return role.permissions