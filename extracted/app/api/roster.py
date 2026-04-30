from fastapi import APIRouter, Query
from typing import Optional
import sqlite3
import os

router = APIRouter(prefix="/roster", tags=["花名册"])

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "attendance.db")


@router.get("/")
def list_roster(
    skip: int = 0,
    limit: int = Query(default=100, le=5000),
    search: Optional[str] = None,
    department: Optional[str] = None,
    position: Optional[str] = None,
    employee_type: Optional[str] = None,
    status: Optional[str] = None,
):
    """花名册列表"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    conditions = []
    params = []
    if search:
        conditions.append("(工号 LIKE ? OR 姓名 LIKE ? OR 岗位 LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if department:
        conditions.append("部门 = ?")
        params.append(department)
    if position:
        conditions.append("岗位 = ?")
        params.append(position)
    if employee_type:
        conditions.append("用工形式 = ?")
        params.append(employee_type)
    # 花名册默认只显示在职人员（是否在职=1）
    # "全部"时不过滤状态，显示所有人
    if status == "left":
        conditions.append("是否在职 = 0")
    elif status == "probation":
        conditions.append("是否在职 = 1 AND 试用到期日 IS NOT NULL AND 试用到期日 != '' AND 试用到期日 != '无' AND date(试用到期日) >= date('now')")
    elif status == "employed":
        conditions.append("是否在职 = 1 AND (试用到期日 IS NULL OR 试用到期日 = '' OR 试用到期日 = '无' OR date(试用到期日) < date('now'))")
    elif status == "all":
        pass  # 不过滤，显示所有人
    else:
        conditions.append("是否在职 = 1")

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    cursor.execute(f"SELECT COUNT(*) FROM roster {where}", params)
    total = cursor.fetchone()[0]

    cursor.execute(
        f"""SELECT * FROM roster {where}
        ORDER BY ROWID DESC LIMIT ? OFFSET ?""",
        params + [limit, skip]
    )
    rows = cursor.fetchall()
    conn.close()

    return {"total": total, "items": [dict(r) for r in rows]}


@router.get("/summary")
def roster_summary():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM roster")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT 部门, COUNT(*) as count
        FROM roster
        WHERE 部门 IS NOT NULL AND 部门 != ''
        GROUP BY 部门
        ORDER BY count DESC
    """)
    dept_stats = [{"department": r["部门"], "count": r["count"]} for r in cursor.fetchall()]

    cursor.execute("""
        SELECT 公积金标准, COUNT(*) as count
        FROM roster
        WHERE 公积金标准 IS NOT NULL AND 公积金标准 != ''
        GROUP BY 公积金标准
        ORDER BY count DESC
    """)
    provident_stats = [{"value": r["公积金标准"], "count": r["count"]} for r in cursor.fetchall()]

    conn.close()
    return {"total": total, "by_department": dept_stats, "by_provident": provident_stats}


@router.get("/departments")
def roster_departments():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT 部门
        FROM roster
        WHERE 部门 IS NOT NULL AND 部门 != ''
        ORDER BY 部门
    """)
    result = [r[0] for r in cursor.fetchall()]
    conn.close()
    return result


@router.get("/positions")
def roster_positions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT 岗位
        FROM roster
        WHERE 岗位 IS NOT NULL AND 岗位 != ''
        ORDER BY 岗位
    """)
    result = [r[0] for r in cursor.fetchall()]
    conn.close()
    return result


@router.get("/lookup")
def roster_lookup(q: str):
    """根据工号或姓名精确查找花名册人员信息，返回第一条"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM roster
        WHERE 工号 = ? OR 姓名 = ?
        ORDER BY ROWID DESC LIMIT 1
    """, [q, q])
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None
