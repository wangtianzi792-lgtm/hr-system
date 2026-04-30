"""通知 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.notification import Notification
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["通知"])


class NotificationCreate:
    """用于内部创建通知"""
    def __init__(self, user_id: int, title: str, content: str = None,
                 type: str = "info", related_id: int = None, related_type: str = None):
        self.user_id = user_id
        self.title = title
        self.content = content
        self.type = type
        self.related_id = related_id
        self.related_type = related_type


@router.get("/")
def list_notifications(
    user_id: int,
    is_read: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取用户的通知列表"""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    total = query.count()
    items = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "items": [
            {
                "id": n.id,
                "title": n.title,
                "content": n.content,
                "type": n.type,
                "is_read": n.is_read,
                "related_id": n.related_id,
                "related_type": n.related_type,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in items
        ]
    }


@router.get("/unread-count")
def get_unread_count(user_id: int, db: Session = Depends(get_db)):
    """获取未读通知数量"""
    count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).count()
    return {"count": count}


@router.put("/{notification_id}/read")
def mark_as_read(notification_id: int, db: Session = Depends(get_db)):
    """标记通知为已读"""
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="通知不存在")
    notif.is_read = True
    db.commit()
    return {"message": "已标记为已读"}


@router.put("/read-all")
def mark_all_as_read(user_id: int, db: Session = Depends(get_db)):
    """标记所有通知为已读"""
    db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"message": "已全部标记为已读"}


def create_notification(db: Session, user_id: int, title: str, content: str = None,
                        type: str = "info", related_id: int = None, related_type: str = None):
    """创建通知的辅助函数（供其他模块调用）"""
    notif = Notification(
        user_id=user_id,
        title=title,
        content=content,
        type=type,
        related_id=related_id,
        related_type=related_type,
    )
    db.add(notif)
    db.commit()
    return notif
