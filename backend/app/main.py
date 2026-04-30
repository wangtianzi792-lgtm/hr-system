from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import logging
import os

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.security import hash_password
from app.api import api_router
from app.models.user import User
from app.models.role import Role

logger = logging.getLogger(__name__)

# 前端静态文件目录 - extracted/app/static 有 Vue App 版本（banner.mp4 + logo）
FRONTEND_DIST = '/extracted/app/static'
index_html = os.path.join(FRONTEND_DIST, 'index.html') if os.path.isdir(FRONTEND_DIST) else None


def init_db():
    """创建数据库表 + 默认管理员账号"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 先创建 admin 角色
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", display_name="管理员", description="系统管理员角色")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            logger.info("Admin role created")
        
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@seashine.com",
                hashed_password=hash_password("admin123"),
                full_name="系统管理员",
                role_id=admin_role.id,
                is_superuser=True,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            logger.info("Default admin created: admin / admin123")
        else:
            logger.info("Admin account exists")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="海昌新材 · 基于 ZKTeco xFace100 的人事考勤系统",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/")
def root():
    if index_html and os.path.isfile(index_html):
        return FileResponse(index_html)
    return {"message": "Welcome to Attendance System", "version": settings.APP_VERSION}


# SPA fallback: 404 时返回 index.html（仅对非 API 路径）
@app.exception_handler(StarletteHTTPException)
async def spa_404_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404 and FRONTEND_DIST and os.path.isdir(FRONTEND_DIST):
        file_path = os.path.join(FRONTEND_DIST, request.url.path.lstrip("/"))
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        if index_html and os.path.isfile(index_html) and not request.url.path.startswith("/api"):
            return FileResponse(index_html)
    # 其他情况返回原始 JSON 错误
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
