"""认证登录 API"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.security import verify_password, hash_password, create_access_token, decode_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, UserInfoResponse, ChangePasswordRequest

router = APIRouter(prefix="/auth", tags=["认证登录"])
logger = logging.getLogger(__name__)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """从 token 获取当前用户"""
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录", headers={"WWW-Authenticate": "Bearer"})
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token已过期", headers={"WWW-Authenticate": "Bearer"})
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效Token", headers={"WWW-Authenticate": "Bearer"})
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用", headers={"WWW-Authenticate": "Bearer"})
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """要求是管理员"""
    if not (current_user.is_superuser or current_user.role == "admin"):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


@router.post("/login", response_model=LoginResponse)
def login(auth: LoginRequest, db: Session = Depends(get_db)):
    """用户名密码登录"""
    user = db.query(User).filter(User.username == auth.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not verify_password(auth.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="账号已被禁用")

    # 更新登录信息
    user.last_login = datetime.now()
    user.login_count = (user.login_count or 0) + 1
    db.commit()

    # 生成 token
    token = create_access_token(data={"sub": str(user.id), "username": user.username, "role": user.role})
    return LoginResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        nickname=user.full_name,
        role=user.role
    )


@router.post("/login/form")
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 标准表单登录（/docs 调试用）"""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="账号已被禁用")
    token = create_access_token(data={"sub": str(user.id), "username": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserInfoResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return UserInfoResponse(
        id=current_user.id,
        username=current_user.username,
        nickname=current_user.full_name,
        role=current_user.role,
    )


@router.post("/password")
def change_password(req: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """修改密码"""
    if not verify_password(req.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="原密码错误")
    current_user.hashed_password = hash_password(req.new_password)
    db.commit()
    return {"message": "密码修改成功"}


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """登出（前端删除token即可，服务端无需处理）"""
    return {"message": "已退出登录"}
