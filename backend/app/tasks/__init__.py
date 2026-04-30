from .attendance_tasks import (
    collect_all_attendance,
    collect_device_attendance,
    generate_daily_report,
    generate_weekly_report,
    generate_monthly_report,
    backup_database,
    sync_device_time,
)

__all__ = [
    "collect_all_attendance",
    "collect_device_attendance",
    "generate_daily_report",
    "generate_weekly_report",
    "generate_monthly_report",
    "backup_database",
    "sync_device_time",
]
