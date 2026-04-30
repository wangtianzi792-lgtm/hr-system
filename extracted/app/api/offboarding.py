from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import sqlite3
import os
from datetime import datetime

router = APIRouter(prefix="/offboarding", tags=["离职管理"])
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "attendance.db")

MANAGER_KEYWORDS = ["经理", "总监", "总经理", "副总经理", "董事长", "总裁", "VP"]


def is_manager_level(position: str) -> bool:
    if not position:
        return False
    p = position.upper()
    return any(k.upper() in p for k in MANAGER_KEYWORDS)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/")
def list_offboarding(
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
        conditions.append("审批状态 = ?")
        params.append(status)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM offboarding {where}", params)
    total = cursor.fetchone()[0]
    cursor.execute(f"""SELECT * FROM offboarding {where} ORDER BY ROWID DESC LIMIT ? OFFSET ?""", params + [limit, skip])
    rows = cursor.fetchall()
    conn.close()
    return {"total": total, "items": [dict(r) for r in rows]}


@router.post("/")
def create_offboarding(data: dict):
    conn = get_conn()
    cursor = conn.cursor()
    cols = ["工号","姓名","性别","联系电话","部门","岗位","离职日期","状态","离职原因","备注","登记人","登记日期"]
    fields = cols + ["审批状态"]
    placeholders = ",".join(["?"] * len(fields))
    values = [data.get(c, "") for c in cols] + ["pending"]
    cursor.execute(f"INSERT INTO offboarding ({','.join(fields)}) VALUES ({placeholders})", values)
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id}


@router.put("/{id}")
def update_offboarding(id: int, data: dict):
    conn = get_conn()
    cursor = conn.cursor()
    updates = [f"{k} = ?" for k in data.keys() if k != "id"]
    vals = [data[k] for k in data.keys() if k != "id"] + [id]
    cursor.execute(f"UPDATE offboarding SET {','.join(updates)} WHERE id = ?", vals)
    conn.commit()
    conn.close()
    return {"success": True}


@router.delete("/{id}")
def delete_offboarding(id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM offboarding WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "离职记录已删除"}


@router.post("/{id}/approve_dept")
def approve_dept(id: int, data: dict):
    """部门级审批"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM offboarding WHERE id = ?", (id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="记录不存在")

    current_status = row["审批状态"] if "审批状态" in row.keys() else row["状态"]
    if current_status not in ("pending",):
        conn.close()
        raise HTTPException(status_code=400, detail="当前状态不允许部门审批")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    approved = data.get("approved", True)
    comment = data.get("comment", "")

    if approved:
        new_status = "dept_approved"
    else:
        new_status = "rejected"

    cursor.execute(f"""UPDATE offboarding SET 审批状态=?, 部门审批人=?, 部门审批意见=?, 部门审批时间=? WHERE id=?""",
        (new_status, data.get("approver", ""), comment, now, id))
    conn.commit()
    conn.close()
    return {"message": "部门审批完成"}


@router.post("/{id}/approve_gm")
def approve_gm(id: int, data: dict):
    """总经理级审批（经理级及以上岗位专用）"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM offboarding WHERE id = ?", (id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="记录不存在")

    current_status = row["审批状态"] if "审批状态" in row.keys() else row["状态"]
    if current_status != "dept_approved":
        conn.close()
        raise HTTPException(status_code=400, detail="需要先完成部门审批")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    approved = data.get("approved", True)
    comment = data.get("comment", "")

    if approved:
        new_status = "gm_approved"
    else:
        new_status = "rejected"

    cursor.execute(f"""UPDATE offboarding SET 审批状态=?, 总经理审批人=?, 总经理审批意见=?, 总经理审批时间=? WHERE id=?""",
        (new_status, data.get("approver", ""), comment, now, id))
    conn.commit()
    conn.close()
    return {"message": "总经理审批完成"}


@router.post("/{id}/approve_hr")
def approve_hr(id: int, data: dict):
    """人事级审批：
    - 经理级及以上：需要部门→总经理→人事三级审批
    - 普通员工：只需要部门→人事两级审批
    """
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM offboarding WHERE id = ?", (id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="记录不存在")

    current_status = row["审批状态"] if "审批状态" in row.keys() else row["状态"]
    position = row["岗位"] if "岗位" in row.keys() else ""

    if is_manager_level(position):
        # 经理级：需要 dept_approved → gm_approved → 人事审批
        if current_status != "gm_approved":
            conn.close()
            raise HTTPException(status_code=400, detail="需要先完成总经理审批")
    else:
        # 普通员工：只需要 dept_approved → 人事审批
        if current_status != "dept_approved":
            conn.close()
            raise HTTPException(status_code=400, detail="需要先完成部门审批")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    approved = data.get("approved", True)
    comment = data.get("comment", "")

    if approved:
        new_status = "confirmed"
        cursor.execute(f"""UPDATE offboarding SET 审批状态=?, 状态=?, 人事审批人=?, 人事审批意见=?, 人事审批时间=? WHERE id=?""",
            (new_status, "confirmed", data.get("approver", "人事审批人"), comment, now, id))
        emp_no = row["工号"]
        if emp_no:
            # 标记为非在职，离职档案在员工管理"离职"筛选中可见
            cursor.execute("UPDATE roster SET 是否在职=0 WHERE 工号=?", (emp_no,))
    else:
        new_status = "rejected"
        cursor.execute(f"""UPDATE offboarding SET 审批状态=?, 状态=?, 人事审批人=?, 人事审批意见=?, 人事审批时间=? WHERE id=?""",
            (new_status, "rejected", data.get("approver", ""), comment, now, id))

    conn.commit()
    conn.close()
    return {"message": "人事审批完成"}


@router.post("/{id}/withdraw")
def withdraw_offboarding(id: int, data: dict):
    """撤回离职申请：
    - 人事审批确认后撤回（confirmed）：恢复入职，职次数+1
    - 其他状态撤回：仅删除离职记录，不影响在职状态
    """
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM offboarding WHERE id = ?", (id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="记录不存在")


    emp_no = row["工号"]
    status = row["审批状态"] if "审批状态" in row.keys() else row["状态"]

    # 只有已确认离职的撤回才算再次入职
    if emp_no and status == "confirmed":
        cursor.execute("SELECT 入职次数 FROM roster WHERE 工号 = ?", (emp_no,))
        emp = cursor.fetchone()
        if emp:
            current_count = emp["入职次数"] or 1
            cursor.execute("UPDATE roster SET 是否在职=1, 入职次数=? WHERE 工号=?",
                (current_count + 1, emp_no))
            # 同步更新 employees 表
            cursor.execute("UPDATE employees SET status='active', is_active=1 WHERE employee_no=?",
                (emp_no,))
        # 清空离职相关信息
        cursor.execute("UPDATE roster SET 离职日期=NULL, 离职原因=NULL WHERE 工号=?", (emp_no,))

    cursor.execute("DELETE FROM offboarding WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"message": "撤回成功"}
