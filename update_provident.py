#!/usr/bin/env python3
"""从花名册更新员工的公积金标准字段，按姓名+部门匹配"""
import openpyxl
import sqlite3

DB_PATH = "/Users/jiuhua/HR系统/extracted/attendance.db"
ROSTER_PATH = "/Users/jiuhua/2026年海昌花名册.xlsx"


def main():
    wb = openpyxl.load_workbook(ROSTER_PATH, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    headers = rows[0]

    col_map = {h: i for i, h in enumerate(headers) if h is not None}
    name_col = col_map.get("姓名")
    dept_col = col_map.get("部门")
    provident_col = col_map.get("公积金（标准）")

    if not name_col or not provident_col:
        print("错误：找不到姓名或公积金列")
        return

    print(f"姓名列: {name_col}, 部门列: {dept_col}, 公积金列: {provident_col}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 获取所有员工：(姓名, 部门ID) → id
    cursor.execute("""
        SELECT e.id, e.name, e.department_id, d.name as dept_name
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
    """)
    emp_map = {}
    for row in cursor.fetchall():
        key = (row[1].strip(), row[2])  # (name, dept_id)
        emp_map[key] = row[0]

    print(f"数据库中有 {len(emp_map)} 名员工")

    # 也建一个纯姓名→ID的映射（备用）
    name_map = {}
    cursor.execute("SELECT id, name FROM employees")
    for row in cursor.fetchall():
        name_map[row[1].strip()] = row[0]

    updated = 0
    matched_by_name_dept = 0
    matched_by_name_only = 0

    for row in rows[1:]:
        name = str(row[name_col]).strip() if row[name_col] else ""
        provident = row[provident_col]
        dept_name = str(row[dept_col]).strip() if dept_col and row[dept_col] else ""

        if not name or str(name) == "None":
            continue

        # 尝试用姓名+部门匹配
        matched_id = None
        if dept_name:
            # 先找部门ID
            cursor.execute("SELECT id FROM departments WHERE name = ?", (dept_name,))
            dept_rows = cursor.fetchall()
            if dept_rows:
                key = (name, dept_rows[0][0])
                matched_id = emp_map.get(key)

        # 备用：纯姓名匹配
        if not matched_id:
            matched_id = name_map.get(name)
            if matched_id:
                matched_by_name_only += 1

        if matched_id:
            cursor.execute(
                "UPDATE employees SET provident_fund = ? WHERE id = ?",
                (str(provident) if provident is not None else None, matched_id)
            )
            if matched_id:
                updated += 1

    conn.commit()

    cursor.execute("SELECT DISTINCT provident_fund FROM employees LIMIT 10")
    results = cursor.fetchall()
    print(f"\n更新后公积金唯一值: {[r[0] for r in results]}")
    print(f"按姓名+部门匹配: {matched_by_name_dept}, 按姓名匹配: {matched_by_name_only}")

    conn.close()
    wb.close()


if __name__ == "__main__":
    main()