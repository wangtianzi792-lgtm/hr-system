from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="设备名称")
    ip_address = Column(String(15), nullable=False, comment="IP地址")
    port = Column(Integer, default=4370, comment="端口")
    device_type = Column(String(50), default="xFace100", comment="设备型号")
    serial_number = Column(String(100), nullable=True, comment="序列号")
    status = Column(String(20), default="offline", comment="状态: online/offline")
    last_sync = Column(DateTime, nullable=True, comment="最后同步时间")
    location = Column(String(200), nullable=True, comment="安装位置")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
