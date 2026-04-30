#!/usr/bin/env python3
"""
导入 Excel 原始打卡记录 → raw_punch_records
"""
import sqlite3
import openpyxl
import os
from datetime import datetime, timedelta, time as dt_time

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendance.db")
EXCEL_PATH = "/Users/jiuhua/Desktop/原始打卡记录日报_2026-04-01-2026-04-02.xlsx"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_dept_map(db):
    mapping = {
        'EHS': 2, 'MIM事业部': 12, 'MIM制造课': 12, 'MIM品质课': 12,
        'MIM技术开发课': 12, '人力资源课': 8, '信息中心部': 9,
        '加工课': 10, '包装课': 10, '品保课': 11, '品管课': 11,
        '外协课': 10, '工务课': 10, '总务课': 10, '总经理室': 1,
        '成形课': 10, '技术研发部': 5, '油浸课': 10, '海荣-成形课': 14,
        '海荣软磁事业部': 14, '烧结课': 10, '热处理课': 10,
        '生产运营部': 10, '生管课': 10, '研磨课': 10,
        '精齿': 13, '精齿-开发课': 13, '精齿-机加工课': 13,
        '营管课': 4, '营销课': 4, '证券部': 3, '财务部': 7,
        '采购课': 6, '金型课': 10,
    }
    cursor = db.cursor()
    valid = {}
    for name, did in mapping.items():
        cursor.execute("SELECT id FROM departments WHERE id = ?", (did,))
        if cursor.fetchone():
            valid[name] = did
        else:
            print(f"  部门 {name}→{did} 不在DB中")
    return valid


def get_emp_map(db):
    cursor = db.cursor()
    cursor.execute("SELECT id, employee_no FROM employees")
    return {str(row["employee_no"]): row["id"] for row in cursor.fetchall()}


def parse_time(t):
    if not t or str(t).strip() == "":
        return None
    t = str(t).strip()
    try:
        if len(t) == 5:
            return datetime.strptime(t, "%H:%M").time()
        elif len(t) == 8:
            return datetime.strptime(t, "%H:%M:%S").time()
    except:
        return None


def main():
    print("=" * 50)
    print("导入打卡记录")
    db = get_db()

    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM raw_punch_records")
    existing = cursor.fetchone()[0]
    if existing > 0:
        print(f"raw_punch_records 已有 {existing} 条，删除后重新导入(y)? ", end="")
        if input().strip().lower() != "y":
            print("退出")
            return
        cursor.execute("DELETE FROM raw_punch_records")
        db.commit()
        print("已清空")

    dept_map = get_dept_map(db)
    emp_map = get_emp_map(db)
    print(f"部门映射: {len(dept_map)} | 员工映射: {len(emp_map)}")

    wb = openpyxl.load_workbook(EXCEL_PATH)
    ws = wb["打卡记录_日报"]

    rows = []
    emp_days = {}  # (emp_id, date) → [punch_times]
    emp_info = {}  # (emp_id, date) → (name, emp_no, dept_name, dept_id)

    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue
        name, emp_no, position, dept_name, punch_date, weekday = row[0], row[1], row[2], row[3], row[4], row[5]
        if not emp_no:
            continue

        emp_no = str(emp_no).strip()
        if emp_no not in emp_map:
            continue

        emp_id = emp_map[emp_no]
        dept_id = dept_map.get(dept_name, 1)
        date_str = str(punch_date)[:10]

        key = (emp_id, date_str)
        if key not in emp_days:
            emp_days[key] = []
            emp_info[key] = (name, emp_no, dept_name, dept_id)

        for p in row[6:11]:
            t = parse_time(p)
            if t:
                emp_days[key].append(t)

    # 写入 raw_punch_records（每人每天逐条）
    cursor = db.cursor()
    count = 0
    for (emp_id, date_str), times in emp_days.items():
        times.sort()
        name, emp_no, dept_name, dept_id = emp_info[(emp_id, date_str)]

        for pt in times:
            punch_dt = datetime.combine(
                datetime.strptime(date_str, "%Y-%m-%d").date(), pt
            )
            rows.append((
                emp_id, 1,
                punch_dt.strftime("%Y-%m-%d %H:%M:%S"),
                0, 0, None, 0, 0, None,
                f"{name}|{emp_no}|{dept_name}"
            ))
            count += 1

    cursor.executemany("""
        INSERT INTO raw_punch_records
        (employee_id, device_id, punch_time, verify_type, punch_method,
         attendance_record_id, is_processed, is_anomaly, anomaly_reason, raw_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)

    db.commit()
    print(f"\n✅ 导入完成：{count} 条打卡记录 ({len(emp_days)} 人天)")


if __name__ == "__main__":
    main()
