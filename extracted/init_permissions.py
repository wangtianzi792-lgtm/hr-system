#!/usr/bin/env python3
"""初始化权限和角色数据"""
import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.models.permission import Permission, RolePermission
from app.models.role import Role

# 定义所有权限
PERMISSIONS = [
    # 系统管理
    {"name": "system.user.manage", "category": "系统管理", "display_name": "用户管理", "description": "创建、编辑、删除用户"},
    {"name": "system.role.manage", "category": "系统管理", "display_name": "角色管理", "description": "创建、编辑、删除角色"},
    {"name": "system.settings", "category": "系统管理", "display_name": "系统设置", "description": "修改系统配置"},
    {"name": "system.logs", "category": "系统管理", "display_name": "操作日志", "description": "查看操作日志"},
    
    # 员工管理
    {"name": "employee.view", "category": "员工管理", "display_name": "员工查看", "description": "查看员工列表和详情"},
    {"name": "employee.create", "category": "员工管理", "display_name": "员工新增", "description": "新增员工"},
    {"name": "employee.edit", "category": "员工管理", "display_name": "员工编辑", "description": "编辑员工信息"},
    {"name": "employee.delete", "category": "员工管理", "display_name": "员工删除", "description": "删除员工"},
    {"name": "employee.export", "category": "员工管理", "display_name": "员工导出", "description": "导出员工数据"},
    
    # 考勤管理
    {"name": "attendance.view", "category": "考勤管理", "display_name": "打卡记录查看", "description": "查看打卡记录"},
    {"name": "attendance.stats", "category": "考勤管理", "display_name": "考勤统计", "description": "查看考勤统计"},
    {"name": "attendance.rule", "category": "考勤管理", "display_name": "考勤规则", "description": "设置考勤规则"},
    
    # 排班管理
    {"name": "schedule.view", "category": "排班管理", "display_name": "班次设置", "description": "设置班次"},
    {"name": "schedule.assign.view", "category": "排班管理", "display_name": "排班表查看", "description": "查看排班表"},
    {"name": "schedule.assign.edit", "category": "排班管理", "display_name": "排班表编辑", "description": "编辑排班表"},
    
    # 请假加班
    {"name": "leave.apply", "category": "请假加班", "display_name": "请假申请", "description": "提交请假申请"},
    {"name": "overtime.apply", "category": "请假加班", "display_name": "加班申请", "description": "提交加班申请"},
    {"name": "leave.approve", "category": "请假加班", "display_name": "请假审批", "description": "审批请假申请"},
    {"name": "overtime.approve", "category": "请假加班", "display_name": "加班审批", "description": "审批加班申请"},
    
    # 考核管理
    {"name": "eval.setup", "category": "考核管理", "display_name": "考核设置", "description": "设置考核周期和维度"},
    {"name": "eval.launch", "category": "考核管理", "display_name": "发起考核", "description": "发起考核流程"},
    {"name": "eval.participate", "category": "考核管理", "display_name": "参与考核", "description": "参与考核评价"},
    {"name": "eval.report", "category": "考核管理", "display_name": "查看考核报告", "description": "查看考核结果"},
    
    # 报表管理
    {"name": "report.daily", "category": "报表管理", "display_name": "日报查看", "description": "查看日报"},
    {"name": "report.monthly", "category": "报表管理", "display_name": "月报查看", "description": "查看月报"},
    {"name": "report.export", "category": "报表管理", "display_name": "导出报表", "description": "导出报表数据"},
]

# 定义角色及其权限
ROLES = [
    {
        "name": "admin",
        "display_name": "超级管理员",
        "description": "拥有系统所有权限",
        "is_system": True,
        "permissions": [p["name"] for p in PERMISSIONS]  # 所有权限
    },
    {
        "name": "hr_manager",
        "display_name": "人事经理",
        "description": "负责人力资源管理",
        "is_system": True,
        "permissions": [
            "employee.view", "employee.create", "employee.edit", "employee.delete", "employee.export",
            "leave.apply", "overtime.apply", "leave.approve", "overtime.approve",
            "eval.setup", "eval.launch", "eval.participate", "eval.report",
            "report.daily", "report.monthly", "report.export",
        ]
    },
    {
        "name": "dept_manager",
        "display_name": "部门主管",
        "description": "管理部门成员",
        "is_system": True,
        "permissions": [
            "employee.view",  # 本部门
            "attendance.view", "attendance.stats",
            "schedule.assign.view",
            "leave.approve", "overtime.approve",
            "eval.participate", "eval.report",
            "report.daily",
        ]
    },
    {
        "name": "employee",
        "display_name": "普通员工",
        "description": "普通员工权限",
        "is_system": True,
        "permissions": [
            "employee.view",  # 本人
            "attendance.view",  # 本人
            "leave.apply", "overtime.apply",
            "eval.participate",
        ]
    },
]

def init():
    db = SessionLocal()
    try:
        # 插入权限
        perm_map = {}
        for p in PERMISSIONS:
            existing = db.query(Permission).filter(Permission.name == p["name"]).first()
            if not existing:
                perm = Permission(**p)
                db.add(perm)
                db.flush()
                perm_map[p["name"]] = perm.id
            else:
                perm_map[p["name"]] = existing.id
        db.commit()
        print(f"插入/更新 {len(PERMISSIONS)} 个权限")
        
        # 插入角色
        role_map = {}
        for r in ROLES:
            perm_ids = r.pop("permissions")
            existing = db.query(Role).filter(Role.name == r["name"]).first()
            if not existing:
                role = Role(**r)
                db.add(role)
                db.flush()
                role_map[r["name"]] = {"id": role.id, "perm_ids": perm_ids}
            else:
                role_map[r["name"]] = {"id": existing.id, "perm_ids": perm_ids}
                # 更新显示名和描述
                existing.display_name = r["display_name"]
                existing.description = r["description"]
        db.commit()
        print(f"插入/更新 {len(ROLES)} 个角色")
        
        # 插入角色-权限关联
        for role_name, role_data in role_map.items():
            # 先删除旧关联
            db.query(RolePermission).filter(RolePermission.role_id == role_data["id"]).delete()
            # 插入新关联
            for perm_name in role_data["perm_ids"]:
                if perm_name in perm_map:
                    rp = RolePermission(role_id=role_data["id"], permission_id=perm_map[perm_name])
                    db.add(rp)
        db.commit()
        print("角色-权限关联已更新")
        
        print("\n✅ 初始化完成!")
        print("\n角色列表:")
        for r in db.query(Role).all():
            print(f"  - {r.display_name} ({r.name})")
        
    finally:
        db.close()

if __name__ == "__main__":
    init()
