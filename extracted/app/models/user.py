from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)

    # 权限
    is_superuser = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    # role_id 已转为 role (VARCHAR) 以兼容现有数据库
    role = Column(String(20), nullable=True)

    # 登录信息
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联关系 - 注释掉以避免外键问题
    # role = relationship("Role", back_populates="users")