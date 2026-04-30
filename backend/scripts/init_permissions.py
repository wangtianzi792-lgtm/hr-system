#!/usr/bin/env python3
"""初始化权限数据：角色和权限"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.models.role import Role
from app.models.permission import Permission, RolePermission

# 定义所有权限 (name, category, display_name, description)
PERMISSIONS = [
    # 用户管理
    ("user:create", "用户管理", "创建用户", "创建新用户账号"),
    ("user:read", "用户管理", "查看用户", "查看用户列表和详情"),
    ("user:update", "用户管理", "编辑用户", "编辑用户信息"),
    ("user:delete", "用户管理", "删除用户", "删除用户账号"),
    ("user:assign_role", "用户管理", "分配角色", "为用户分配角色"),

    # 员工管理
    ("employee:create", "员工管理", "创建员工", "添加新员工"),
    ("employee:read", "员工管理", "查看员工", "查看员工列表"),
    ("employee:update", "员工管理", "编辑员工", "编辑员工信息"),
    ("employee:delete", "员工管理", "删除员工", "删除员工记录"),
    ("employee:enroll", "员工管理", "同步考勤机", "下发人脸/指纹到考勤机"),

    # 部门管理
    ("department:create", "部门管理", "创建部门", "添加新部门"),
    ("department:read", "部门管理", "查看部门", "查看部门列表"),
    ("department:update", "部门管理", "编辑部门", "编辑部门信息"),
    ("department:delete", "部门管理", "删除部门", "删除部门"),

    # 考勤管理
    ("attendance:read", "考勤管理", "查看考勤", "查看考勤记录"),
    ("attendance:collect", "考勤管理", "采集考勤", "从设备采集考勤数据"),
    ("attendance:export", "考勤管理", "导出考勤", "导出考勤报表"),
    ("attendance:summary", "考勤管理", "考勤统计", "考勤汇总统计"),

    # 请假管理
    ("leave:create", "请假管理", "申请请假", "提交请假申请"),
    ("leave:read", "请假管理", "查看请假", "查看请假记录"),
    ("leave:approve", "请假管理", "审批请假", "审批请假申请"),
    ("leave:delete", "请假管理", "删除请假", "删除请假记录"),

    # 排班管理
    ("schedule:read", "排班管理", "查看排班", "查看排班表"),
    ("schedule:manage", "排班管理", "管理排班", "创建和编辑排班"),

    # 设备管理
    ("device:create", "设备管理", "添加设备", "添加新考勤机"),
    ("device:read", "设备管理", "查看设备", "查看设备列表"),
    ("device:update", "设备管理", "编辑设备", "编辑设备信息"),
    ("device:delete", "设备管理", "删除设备", "删除设备"),
    ("device:sync", "设备管理", "同步设备", "同步设备数据"),

    # 系统设置
    ("settings:read", "系统设置", "查看设置", "查看系统设置"),
    ("settings:update", "系统设置", "修改设置", "修改系统设置"),

    # 角色权限管理
    ("role:create", "角色权限", "创建角色", "创建新角色"),
    ("role:read", "角色权限", "查看角色", "查看角色列表"),
    ("role:update", "角色权限", "编辑角色", "编辑角色"),
    ("role:delete", "角色权限", "删除角色", "删除角色"),
    ("role:assign", "角色权限", "分配权限", "为角色分配权限"),

    # 考核管理
    ("evaluation:read", "考核管理", "查看考核", "查看考核记录"),
    ("evaluation:manage", "考核管理", "管理考核", "发起和管理考核"),
    ("evaluation:self", "考核管理", "自评", "填写自评"),
    ("evaluation:peer", "考核管理", "互评", "填写互评"),
    ("evaluation:report", "考核管理", "考核报告", "查看考核报告"),

    # 原始打卡记录查询
    ("raw_record:read", "打卡记录", "查看原始打卡", "查看设备原始打卡记录"),
]

# 定义角色 (name, display_name, description, is_system, sort_order, perm_names)
ROLES = [
    (
        "admin", "超级管理员", "系统最高权限，拥有所有功能",
        True, 1,
        ["*"]  # * = 所有权限
    ),
    (
        "hr", "人事专员", "人事管理权限，可管理员工、考勤、请假、考核",
        True, 2,
        [
            "user:create", "user:read", "user:update",
            "employee:create", "employee:read", "employee:update", "employee:delete", "employee:enroll",
            "department:create", "department:read", "department:update", "department:delete",
            "attendance:read", "attendance:collect", "attendance:export", "attendance:summary",
            "leave:create", "leave:read", "leave:approve", "leave:delete",
            "schedule:read", "schedule:manage",
            "device:create", "device:read", "device:update", "device:delete", "device:sync",
            "evaluation:read", "evaluation:manage", "evaluation:report",
            "raw_record:read",
        ]
    ),
    (
        "manager", "部门主管", "部门管理权限，可查看本部门数据和审批",
        True, 3,
        [
            "employee:read",
            "department:read",
            "attendance:read", "attendance:summary",
            "leave:read", "leave:approve",
            "schedule:read",
            "evaluation:peer", "evaluation:report",
            "raw_record:read",
        ]
    ),
    (
        "employee", "普通员工", "基本员工权限，可查看考勤和提交请假",
        True, 4,
        [
            "employee:read",
            "attendance:read",
            "leave:create", "leave:read",
            "schedule:read",
            "evaluation:self", "evaluation:peer", "evaluation:report",
        ]
    ),
]


def init_permissions():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 创建权限
        perm_map = {}
        for name, category, display_name, description in PERMISSIONS:
            existing = db.query(Permission).filter(Permission.name == name).first()
            if not existing:
                perm = Permission(
                    name=name,
                    category=category,
                    display_name=display_name,
                    description=description
                )
                db.add(perm)
                db.flush()
                perm_map[name] = perm.id
            else:
                perm_map[name] = existing.id
            print(f"  权限: {name}")

        # 创建角色并分配权限
        for role_name, display_name, description, is_system, sort_order, perm_names in ROLES:
            existing = db.query(Role).filter(Role.name == role_name).first()
            if not existing:
                role = Role(
                    name=role_name,
                    display_name=display_name,
                    description=description,
                    is_system=is_system,
                    sort_order=sort_order,
                )
                db.add(role)
                db.flush()
                print(f"\n创建角色: {display_name}")
            else:
                role = existing
                print(f"\n更新角色: {display_name}")

            # 分配权限
            assigned_count = 0
            for perm_name in perm_names:
                if perm_name == "*":
                    # admin 获取所有权限
                    all_perms = db.query(Permission).all()
                    for p in all_perms:
                        existing_rp = db.query(RolePermission).filter(
                            RolePermission.role_id == role.id,
                            RolePermission.permission_id == p.id
                        ).first()
                        if not existing_rp:
                            rp = RolePermission(role_id=role.id, permission_id=p.id)
                            db.add(rp)
                            assigned_count += 1
                else:
                    pid = perm_map.get(perm_name)
                    if pid:
                        existing_rp = db.query(RolePermission).filter(
                            RolePermission.role_id == role.id,
                            RolePermission.permission_id == pid
                        ).first()
                        if not existing_rp:
                            rp = RolePermission(role_id=role.id, permission_id=pid)
                            db.add(rp)
                            assigned_count += 1

            print(f"  分配权限数: {assigned_count}")

        db.commit()
        print("\n权限初始化完成!")
        print(f"   角色数: {len(ROLES)}")
        print(f"   权限数: {len(PERMISSIONS)}")

    except Exception as e:
        db.rollback()
        print(f"\n初始化失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("开始初始化权限数据...")
    init_permissions()