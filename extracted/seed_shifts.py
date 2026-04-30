#!/usr/bin/env python3
"""班次数据初始化脚本"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendance.db")


def seed_shifts():
    if not os.path.exists(DB_PATH):
        print(f"数据库不存在: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 检查是否已有班次数据
    cursor.execute("SELECT COUNT(*) FROM shifts")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"班次表已有 {count} 条数据，跳过初始化。")
        return

    shifts = [
        # (name, shift_type, check_in_start, check_in_end, check_out_start, check_out_end, work_hours, color)
        ("早班", "day", "07:00", "09:00", "17:00", "18:00", "8h", "#1989fa"),
        ("中班", "swing", "15:00", "16:00", "23:00", "23:59", "8h", "#fa8c16"),
        ("晚班", "night", "23:00", "23:59", "07:00", "08:00", "8h", "#722ed1"),
        ("行政班", "day", "09:00", "09:30", "18:00", "18:30", "8.5h", "#52c41a"),
        ("休息班", "off", "00:00", "00:00", "00:00", "00:00", "0h", "#d9d9d9"),
        ("12小时班(白)", "day", "08:00", "09:00", "20:00", "21:00", "12h", "#f5222d"),
        ("12小时班(夜)", "night", "20:00", "21:00", "08:00", "09:00", "12h", "#eb2f96"),
    ]

    sql = """
    INSERT INTO shifts (name, shift_type, check_in_start, check_in_end, check_out_start, check_out_end, work_hours, color, is_active)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
    """

    for shift in shifts:
        cursor.execute(sql, shift)

    conn.commit()
    cursor.execute("SELECT id, name, shift_type, check_in_start, check_out_end FROM shifts")
    print("已初始化的班次：")
    for row in cursor.fetchall():
        print(f"  [{row[0]}] {row[1]} | {row[2]} | 上班:{row[3]} 下班:{row[4]}")

    conn.close()
    print(f"\n共插入 {len(shifts)} 条班次数据 ✅")


if __name__ == "__main__":
    seed_shifts()
