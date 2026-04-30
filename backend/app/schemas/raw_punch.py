from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


class RawPunchResponse(BaseModel):
    id: int
    employee_id: Optional[int] = None
    device_id: Optional[int] = None
    punch_time: datetime
    verify_type: int
    punch_method: int
    is_processed: bool
    is_anomaly: bool
    anomaly_reason: Optional[str] = None
    raw_data: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RawPunchListResponse(BaseModel):
    total: int
    items: List[RawPunchResponse]


class RawPunchMarkAnomalyRequest(BaseModel):
    record_ids: List[int]
    is_anomaly: bool
    anomaly_reason: Optional[str] = None


class RawPunchLinkRequest(BaseModel):
    record_ids: List[int]
    employee_id: int
