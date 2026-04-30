"""通知模型"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Notification(Base):
    """系统通知"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="通知接收人")
    title = Column(String(200), nullable=False, comment="通知标题")
    content = Column(Text, nullable=True, comment="通知内容")
    type = Column(String(50), nullable=False, default="info", comment="通知类型: info/leave/overtime/attendance/salary")
    is_read = Column(Boolean, default=False, comment="是否已读")
    related_id = Column(Integer, nullable=True, comment="关联记录ID（如请假ID）")
    related_type = Column(String(50), nullable=True, comment="关联类型（如 leave_request）")

    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", foreign_keys=[user_id])
