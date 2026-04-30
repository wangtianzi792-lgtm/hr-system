from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DeviceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="设备名称")
    ip_address: str = Field(..., description="IP地址")
    port: int = Field(default=4370, description="端口")
    device_type: str = Field(default="xFace100", description="设备型号")
    location: Optional[str] = Field(None, description="安装位置")


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class DeviceResponse(DeviceBase):
    id: int
    serial_number: Optional[str] = None
    status: str = "offline"
    last_sync: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DeviceStatus(BaseModel):
    device_id: int
    status: str
    user_count: Optional[int] = None
    record_count: Optional[int] = None
    firmware_version: Optional[str] = None
    device_time: Optional[datetime] = None
