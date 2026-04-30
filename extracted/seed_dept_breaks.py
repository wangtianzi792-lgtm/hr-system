#!/usr/bin/env python3
"""初始化所有部门的休息时间（默认 12:00-13:00）"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendance.db")


def seed_dept_breaks():
    if not os.path.exists(DB_PATH):
        print(f"数据库不存在: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 检查 department_breaks 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='department_breaks'")
    if not cursor.fetchone():
        print("表 department_breaks 不存在，请先运行后端让 FastAPI 自动建表")
        return

    # 获取所有部门
    cursor.execute("SELECT id, name FROM departments ORDER BY id")
    departments = cursor.fetchall()

    # 检查已有配置
    cursor.execute("SELECT department_id FROM department_breaks")
    existing = set(row[0] for row in cursor.fetchall())

    count = 0
    for dept_id, dept_name in departments:
        if dept_id in existing:
            continue
        cursor.execute("""
            INSERT INTO department_breaks (department_id, break_start, break_end, break_minutes, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, (dept_id, "12:00", "13:00", 60, 1))
        print(f"  + {dept_name}（ID={dept_id}）: 12:00 - 13:00 (60分钟)")
        count += 1

    conn.commit()

    if count == 0:
        print("所有部门休息时间已配置，无需重复初始化")
    else:
        print(f"\n共为 {count} 个部门初始化休息时间")

    # 验证
    cursor.execute("""
        SELECT d.name, db.break_start, db.break_end, db.break_minutes
        FROM department_breaks db
        JOIN departments d ON d.id = db.department_id
        ORDER BY db.department_id
    """)
    print("\n当前配置：")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} - {row[2]} ({row[3]}分钟)")

    conn.close()


if __name__ == "__main__":
    seed_dept_breaks()
