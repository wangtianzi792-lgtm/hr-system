"""登录/认证相关 Pydantic 模型"""
from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    nickname: Optional[str] = None
    role: Optional[str] = None


class UserInfoResponse(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    role: Optional[str] = None
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
