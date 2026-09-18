"""
Routes package for the API.
Each module in this package represents a group of related endpoints.
"""

from fastapi import APIRouter

from .auth import router as auth_router
from .baseline_schedule import router as baseline_schedule_router
from .daily_schedule import router as daily_schedule_router
from .tasks import router as tasks_router
from .habits import router as habits_router

# Create main router
router = APIRouter()

# Include all route modules
router.include_router(auth_router, prefix="/users", tags=["users"])
router.include_router(baseline_schedule_router, prefix="/baseline_schedule", tags=["schedules"])
router.include_router(daily_schedule_router, prefix="/daily_schedule", tags=["schedules"])
router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
router.include_router(habits_router, prefix="/habits", tags=["habits"]) 