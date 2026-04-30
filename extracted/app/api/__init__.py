from fastapi import APIRouter
from app.api import (
    auth, devices, employees, departments,
    attendance, shifts, leave, dashboard, settings,
    roles, raw_punch, evaluation, department_breaks, roster,
    onboarding, offboarding, work_hours
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(devices.router)
api_router.include_router(employees.router)
api_router.include_router(departments.router)
api_router.include_router(attendance.router)
api_router.include_router(shifts.router)
api_router.include_router(leave.router)
api_router.include_router(dashboard.router)
api_router.include_router(settings.router)
api_router.include_router(roles.router)
api_router.include_router(raw_punch.router)
api_router.include_router(evaluation.router)
api_router.include_router(department_breaks.router)
api_router.include_router(roster.router)
api_router.include_router(onboarding.router)
api_router.include_router(offboarding.router)
api_router.include_router(work_hours.router)
