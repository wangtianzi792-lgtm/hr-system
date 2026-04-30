#!/usr/bin/env python3
"""
根据 raw_punch_records 计算每日工时，写入 attendance_summaries
公式：实际工时 = 下班打卡 - 上班打卡 - 休息时长
"""
import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendance.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_dept_breaks(db):
    """department_id → break_minutes"""
    cursor = db.cursor()
    cursor.execute("SELECT department_id, break_minutes FROM department_breaks")
    return {r["department_id"]: r["break_minutes"] for r in cursor.fetchall()}


def calculate():
    db = get_db()
    breaks = get_dept_breaks(db)

    cursor = db.cursor()

    # 统计原始打卡
    cursor.execute("""
        SELECT
            r.employee_id,
            e.department_id,
            date(r.punch_time) as punch_date,
            min(r.punch_time) as first_punch,
            max(r.punch_time) as last_punch,
            count(*) as punch_count
        FROM raw_punch_records r
        JOIN employees e ON e.id = r.employee_id
        WHERE date(r.punch_time) >= '2026-04-01'
        GROUP BY r.employee_id, date(r.punch_time)
        ORDER BY punch_date, r.employee_id
    """)
    records = cursor.fetchall()

    print(f"找到 {len(records)} 条人天记录，开始计算工时...")

    rows = []
    for r in records:
        emp_id = r["employee_id"]
        dept_id = r["department_id"] or 1
        date_str = r["punch_date"]
        first_str = r["first_punch"]
        last_str = r["last_punch"]
        break_min = breaks.get(dept_id, 60)

        # 解析时间
        first_dt = datetime.strptime(first_str, "%Y-%m-%d %H:%M:%S")
        last_dt = datetime.strptime(last_str, "%Y-%m-%d %H:%M:%S")

        # 跨天情况（如晚班：23:00 → 07:00）
        if last_dt <= first_dt:
            last_dt += timedelta(days=1)

        total_minutes = int((last_dt - first_dt).seconds / 60)
        work_minutes = max(0, total_minutes - break_min)
        work_hours = round(work_minutes / 60, 2)
        overtime_hours = round(max(0, total_minutes - 8 * 60 - break_min) / 60, 2)

        # 迟到/早退判断（简单按9:00前上班算正常，这里暂不标记异常）
        late = 0
        early = 0
        absent = 0

        # 上班超过9:00算迟到
        if first_dt.hour > 9 or (first_dt.hour == 9 and first_dt.minute > 0):
            late = 1

        # 下班早于17:00算早退
        if last_dt.hour < 17 or (last_dt.hour == 17 and last_dt.minute < 30):
            early = 1

        rows.append((
            emp_id, date_str, 1, 1, late, early, absent,
            str(work_hours), str(overtime_hours)
        ))

    # 清空旧记录并写入新记录
    cursor.execute("DELETE FROM attendance_summaries WHERE summary_date >= '2026-04-01'")

    cursor.executemany("""
        INSERT INTO attendance_summaries
        (employee_id, summary_date, work_days, actual_days,
         late_count, early_count, absent_count, total_work_hours, overtime_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)

    db.commit()
    print(f"✅ 工时计算完成：{len(rows)} 条记录")

    # 打印几个示例
    cursor.execute("""
        SELECT s.employee_id, e.name, e.employee_no, s.summary_date,
               s.total_work_hours, s.overtime_hours, s.late_count, s.early_count
        FROM attendance_summaries s
        JOIN employees e ON e.id = s.employee_id
        ORDER BY s.summary_date, e.employee_no
        LIMIT 10
    """)
    print("\n示例数据：")
    print(f"{'姓名':<10} {'工号':<10} {'日期':<12} {'工时':<6} {'加班':<6} {'迟到':<4} {'早退':<4}")
    print("-" * 55)
    for row in cursor.fetchall():
        print(f"{row['name']:<10} {row['employee_no']:<10} {row['summary_date']:<12} "
              f"{row['total_work_hours']:<6} {row['overtime_hours']:<6} "
              f"{row['late_count']:<4} {row['early_count']:<4}")


if __name__ == "__main__":
    calculate()
