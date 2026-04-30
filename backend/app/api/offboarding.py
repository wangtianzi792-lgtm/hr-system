from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from app.core.database import get_db

router = APIRouter(prefix="/offboarding", tags=["离职管理"])


@router.get("/")
def list_offboarding(skip: int = 0, limit: int = 30,
                    keyword: Optional[str] = None,
                    department: Optional[str] = None,
                    status: Optional[str] = None,
                    db: Session = Depends(get_db)):
    from app.models.offboarding import Offboarding
    from sqlalchemy import or_
    query = db.query(Offboarding)
    if keyword:
        query = query.filter(or_(
            Offboarding.工号.contains(keyword),
            Offboarding.姓名.contains(keyword)
        ))
    if department:
        query = query.filter(Offboarding.部门 == department)
    if status:
        query = query.filter(Offboarding.审批状态 == status)
    total = query.count()
    items = query.order_by(Offboarding.id.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [_row_dict(r) for r in items]}


@router.post("/")
def create_offboarding(data: dict, db: Session = Depends(get_db)):
    from app.models.offboarding import Offboarding
    if '审批状态' not in data:
        data['审批状态'] = 'pending'
    record = Offboarding(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return _row_dict(record)


@router.put("/{record_id}")
def update_offboarding(record_id: int, data: dict, db: Session = Depends(get_db)):
    from app.models.offboarding import Offboarding
    record = db.query(Offboarding).filter(Offboarding.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    for key, value in data.items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return _row_dict(record)


@router.delete("/{record_id}")
def delete_offboarding(record_id: int, db: Session = Depends(get_db)):
    from app.models.offboarding import Offboarding
    record = db.query(Offboarding).filter(Offboarding.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(record)
    db.commit()
    return {"message": "删除成功"}


def _is_manager_level(position: str) -> bool:
    if not position:
        return False
    keywords = ['经理', '总监', '总经理', '副总经理', '董事长', '总裁', 'VP', '副总']
    return any(k in position for k in keywords)


def _find_employee_by_no(db: Session, employee_no: str):
    from app.models.employee import Employee
    return db.query(Employee).filter(Employee.employee_no == employee_no).first()


def _row_dict(r):
    return {k: getattr(r, k, None) for k in r.__table__.columns.keys()}


# ===== 部门审批 =====
@router.post("/{record_id}/approve_dept")
def approve_dept(record_id: int, data: dict, db: Session = Depends(get_db)):
    """
    部门审批：只有 pending 状态才能审批。
    - 通过：状态 -> dept_approved（普通员工）/ gm_approved（经理级，跳过GM直接到人事）
    - 拒绝：状态 -> rejected
    """
    from app.models.offboarding import Offboarding
    from datetime import datetime

    record = db.query(Offboarding).filter(Offboarding.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    if record.审批状态 != 'pending':
        raise HTTPException(status_code=400, detail="当前状态不允许部门审批")

    approved = data.get('approved', True)
    approver = data.get('approver', '')
    comment = data.get('comment', '')

    record.部门审批人 = approver
    record.部门审批意见 = comment
    record.部门审批时间 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not approved:
        record.审批状态 = 'rejected'
    elif _is_manager_level(record.岗位):
        # 经理级：部门审批通过后，直接到人事审批（跳过总经理）
        record.审批状态 = 'gm_approved'
    else:
        # 普通员工：部门审批通过后，等待人事审批
        record.审批状态 = 'dept_approved'

    db.commit()
    db.refresh(record)
    return _row_dict(record)


# ===== 总经理审批 =====
@router.post("/{record_id}/approve_gm")
def approve_gm(record_id: int, data: dict, db: Session = Depends(get_db)):
    """
    总经理审批：只有 gm_approved 状态才能审批（仅经理级走此流程）。
    - 通过：状态 -> gm_approved（前端下一步显示人事审批）
    - 拒绝：状态 -> rejected
    """
    from app.models.offboarding import Offboarding
    from datetime import datetime

    record = db.query(Offboarding).filter(Offboarding.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    if record.审批状态 != 'gm_approved':
        raise HTTPException(status_code=400, detail="当前状态不允许总经理审批")

    approved = data.get('approved', True)
    approver = data.get('approver', '')
    comment = data.get('comment', '')

    record.总经理审批人 = approver
    record.总经理审批意见 = comment
    record.总经理审批时间 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not approved:
        record.审批状态 = 'rejected'
    # else: 状态保持 gm_approved，前端显示人事审批按钮

    db.commit()
    db.refresh(record)
    return _row_dict(record)


# ===== 人事审批 =====
@router.post("/{record_id}/approve_hr")
def approve_hr(record_id: int, data: dict, db: Session = Depends(get_db)):
    """
    人事审批（最终确认）：
    - 适用于：dept_approved（普通员工）或 gm_approved（经理级）
    - 通过 + 确认离职：状态 -> confirmed，员工 is_active = False（花名册消失）
    - 拒绝：状态 -> rejected
    """
    from app.models.offboarding import Offboarding
    from datetime import datetime

    record = db.query(Offboarding).filter(Offboarding.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    # 允许审批的状态：dept_approved（非经理）或 gm_approved（经理）
    if record.审批状态 not in ('dept_approved', 'gm_approved'):
        raise HTTPException(status_code=400, detail="当前状态不允许人事审批")

    approved = data.get('approved', True)
    approver = data.get('approver', '')
    comment = data.get('comment', '')

    record.人事审批人 = approver
    record.人事审批意见 = comment
    record.人事审批时间 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not approved:
        record.审批状态 = 'rejected'
    else:
        # 确认离职：状态 -> confirmed，员工从花名册移除
        record.审批状态 = 'confirmed'
        record.状态 = 'confirmed'
        # 找到员工，标记为非在职
        emp = _find_employee_by_no(db, record.工号)
        if emp:
            emp.is_active = False

    db.commit()
    db.refresh(record)
    return _row_dict(record)


# ===== 撤回 =====
@router.post("/{record_id}/withdraw")
def withdraw_offboarding(record_id: int, data: dict, db: Session = Depends(get_db)):
    """
    撤回离职申请：
    - pending / dept_approved / gm_approved：状态 -> withdrawn，员工不受影响
    - confirmed（已确认离职）：状态 -> withdrawn，恢复员工 is_active = True（重新出现在花名册）
    """
    from app.models.offboarding import Offboarding
    from datetime import datetime

    record = db.query(Offboarding).filter(Offboarding.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    if record.审批状态 == 'withdrawn':
        raise HTTPException(status_code=400, detail="已撤回，不能重复操作")

    # 如果已确认离职，需要恢复员工状态
    if record.审批状态 == 'confirmed':
        emp = _find_employee_by_no(db, record.工号)
        if emp:
            emp.is_active = True
            emp.status = 'active'
        # 同步更新 roster 表
        db.execute(text("UPDATE roster SET 是否在职=1 WHERE 工号=:no"), {"no": record.工号})
        # 入职次数 +1
        db.execute(text("UPDATE roster SET 入职次数=入职次数+1 WHERE 工号=:no"), {"no": record.工号})
        # 更新离职日期为NULL
        db.execute(text("UPDATE roster SET 离职日期=NULL, 离职原因=NULL WHERE 工号=:no"), {"no": record.工号})

    record.审批状态 = 'withdrawn'
    db.commit()
    # 撤回后删除记录（不留在列表里）
    db.delete(record)
    db.commit()
    return {"message": "撤回成功"}
