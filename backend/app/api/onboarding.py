from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db

router = APIRouter(prefix="/onboarding", tags=["入职管理"])


@router.get("/")
def list_onboarding(skip: int = 0, limit: int = 30,
                   keyword: Optional[str] = None,
                   department: Optional[str] = None,
                   status: Optional[str] = None,
                   db: Session = Depends(get_db)):
    from app.models.onboarding import Onboarding
    query = db.query(Onboarding)
    if keyword:
        from sqlalchemy import or_
        query = query.filter(or_(
            Onboarding.工号.contains(keyword),
            Onboarding.姓名.contains(keyword)
        ))
    if department:
        query = query.filter(Onboarding.部门 == department)
    if status:
        query = query.filter(Onboarding.状态 == status)
    total = query.count()
    items = query.order_by(Onboarding.id.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [_row_dict(r) for r in items]}


@router.post("/")
def create_onboarding(data: dict, db: Session = Depends(get_db)):
    from app.models.onboarding import Onboarding
    record = Onboarding(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return _row_dict(record)


@router.put("/{record_id}")
def update_onboarding(record_id: int, data: dict, db: Session = Depends(get_db)):
    from app.models.onboarding import Onboarding
    record = db.query(Onboarding).filter(Onboarding.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    for key, value in data.items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return _row_dict(record)


@router.delete("/{record_id}")
def delete_onboarding(record_id: int, db: Session = Depends(get_db)):
    from app.models.onboarding import Onboarding
    record = db.query(Onboarding).filter(Onboarding.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(record)
    db.commit()
    return {"message": "删除成功"}


def _row_dict(r):
    return {k: getattr(r, k, None) for k in r.__table__.columns.keys()}
