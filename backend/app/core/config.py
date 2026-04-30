from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "人事考勤系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # 数据库配置（开发环境用SQLite，生产环境用PostgreSQL）
    DATABASE_URL: str = "sqlite:///./attendance.db"
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 考勤机配置
    ZK_DEFAULT_PORT: int = 4370
    ZK_DEFAULT_TIMEOUT: int = 5
    
    # Celery 配置（从 REDIS_URL 派生）
    @property
    def CELERY_BROKER_URL(self) -> str:
        return self.REDIS_URL
    
    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return self.REDIS_URL
    
    # 备份配置
    BACKUP_DIR: str = "/app/backups"
    BACKUP_RETENTION_DAYS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
