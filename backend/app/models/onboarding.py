from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Onboarding(Base):
    __tablename__ = "onboarding"

    id = Column(Integer, primary_key=True, autoincrement=True)
    工号 = Column(String(50), nullable=True)
    姓名 = Column(String(100), nullable=True)
    性别 = Column(String(10), nullable=True)
    联系电话 = Column(String(50), nullable=True)
    部门 = Column(String(100), nullable=True)
    岗位 = Column(String(100), nullable=True)
    职务级别 = Column(String(50), nullable=True)
    入职日期 = Column(String(20), nullable=True)
    状态 = Column(String(20), default='pending')
    备注 = Column(Text, nullable=True)
    登记人 = Column(String(100), nullable=True)
    登记日期 = Column(String(20), nullable=True)
