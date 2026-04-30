from fastapi import APIRouter, Query
from typing import Optional
import sqlite3
import os

router = APIRouter(prefix="/onboarding", tags=["入职管理"])
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "attendance.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/")
def list_onboarding(
    skip: int = 0,
    limit: int = Query(default=100, le=5000),
    search: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
):
    conditions = []
    params = []
    if search:
        conditions.append("(工号 LIKE ? OR 姓名 LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])
    if department:
        conditions.append("部门 = ?")
        params.append(department)
    if status:
        conditions.append("状态 = ?")
        params.append(status)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM onboarding {where}", params)
    total = cursor.fetchone()[0]
    cursor.execute(f"""SELECT * FROM onboarding {where} ORDER BY ROWID DESC LIMIT ? OFFSET ?""", params + [limit, skip])
    rows = cursor.fetchall()
    conn.close()
    return {"total": total, "items": [dict(r) for r in rows]}


@router.post("/")
def create_onboarding(data: dict):
    conn = get_conn()
    cursor = conn.cursor()
    cols = ["工号","姓名","性别","联系电话","部门","岗位","入职日期","状态","备注","登记人","登记日期"]
    fields = ",".join(cols)
    placeholders = ",".join(["?"] * len(cols))
    values = [data.get(c, "") for c in cols]
    cursor.execute(f"INSERT INTO onboarding ({fields}) VALUES ({placeholders})", values)
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id}


@router.put("/{id}")
def update_onboarding(id: int, data: dict):
    conn = get_conn()
    cursor = conn.cursor()
    updates = [f"{k} = ?" for k in data.keys() if k != "id"]
    vals = [data[k] for k in data.keys() if k != "id"] + [id]
    cursor.execute(f"UPDATE onboarding SET {','.join(updates)} WHERE id = ?", vals)
    conn.commit()
    conn.close()
    return {"success": True}


@router.delete("/{id}")
def delete_onboarding(id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM onboarding WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"success": True}
