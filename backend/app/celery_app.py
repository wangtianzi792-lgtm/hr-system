from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# 创建 Celery 应用
celery_app = Celery(
    "attendance",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.attendance_tasks"]
)

# Celery 配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    beat_schedule={
        # 每5分钟采集考勤数据
        "collect-attendance": {
            "task": "app.tasks.attendance_tasks.collect_all_attendance",
            "schedule": 300.0,  # 5分钟
        },
        # 每天凌晨生成日报
        "generate-daily-report": {
            "task": "app.tasks.attendance_tasks.generate_daily_report",
            "schedule": crontab(hour=1, minute=0),  # 每天凌晨1点
        },
        # 每周一凌晨生成周报
        "generate-weekly-report": {
            "task": "app.tasks.attendance_tasks.generate_weekly_report",
            "schedule": crontab(day_of_week=1, hour=2, minute=0),  # 每周一凌晨2点
        },
        # 每月1号生成月报
        "generate-monthly-report": {
            "task": "app.tasks.attendance_tasks.generate_monthly_report",
            "schedule": crontab(day_of_month=1, hour=3, minute=0),  # 每月1号凌晨3点
        },
        # 每天凌晨备份数据库
        "backup-database": {
            "task": "app.tasks.attendance_tasks.backup_database",
            "schedule": crontab(hour=0, minute=30),  # 每天凌晨0:30
        },
    }
)
