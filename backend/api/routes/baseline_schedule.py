from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from tzlocal import get_localzone
import logging

from database import get_db_context
from database.models import User, BaselineSchedule
from utils import TimeUtils

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Request Models
from pydantic import BaseModel

class BaselineTaskRequest(BaseModel):
    task_name: str
    scheduled_time: str
    goal_time: Optional[str] = None

class BaselineScheduleRequest(BaseModel):
    user_id: int
    tasks: List[BaselineTaskRequest]

@router.post("/set")
def set_baseline_schedule(request: BaselineScheduleRequest, db: Session = Depends(get_db_context)):
    """Stores the user's baseline schedule with times converted to UTC."""
    
    user_id = request.user_id
    tasks = request.tasks

    # Detect User's System Timezone
    user_current_tz = str(get_localzone())
    if not TimeUtils.validate_timezone(user_current_tz):
        raise HTTPException(status_code=400, detail="Invalid timezone detected.")

    # Delete old baseline schedule before inserting new tasks
    db.query(BaselineSchedule).filter(BaselineSchedule.user_id == user_id).delete()

    new_tasks = []
    for task in tasks:
        # Convert local scheduled time to UTC
        try:
            scheduled_time = TimeUtils.parse_time_string(task.scheduled_time)
            goal_time = TimeUtils.parse_time_string(task.goal_time) if task.goal_time else None

            new_task = BaselineSchedule(
                user_id=user_id,
                task_name=task.task_name,
                scheduled_time=scheduled_time,
                goal_time=goal_time,
                user_timezone=user_current_tz
            )
            db.add(new_task)
            new_tasks.append(new_task)
        except Exception as e:
            logger.error(f"Error processing task {task.task_name}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid time format for task {task.task_name}")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save baseline schedule")

    return {
        "message": "Baseline schedule set successfully.",
        "detected_timezone": user_current_tz,
        "tasks": [{"task_name": t.task_name, "scheduled_time": str(t.scheduled_time), 
                   "goal_time": str(t.goal_time) if t.goal_time else None} for t in new_tasks]
    }

@router.get("/{user_id}")
def get_baseline_schedule(user_id: int, request: Request, db: Session = Depends(get_db_context)):
    """Fetches the user's baseline schedule and adjusts times to their current timezone."""

    tasks = db.query(BaselineSchedule).filter(BaselineSchedule.user_id == user_id).all()
    if not tasks:
        return {"message": "No baseline schedule found."}

    # Get User's Current Timezone from Request Headers or fallback to stored
    user_current_tz = request.headers.get("User-Timezone")
    if not user_current_tz:
        user_current_tz = tasks[0].user_timezone

    if not TimeUtils.validate_timezone(user_current_tz):
        raise HTTPException(status_code=400, detail="Invalid timezone.")

    # Convert times to user's timezone
    adjusted_tasks = []
    for task in tasks:
        adjusted_tasks.append({
            "task_name": task.task_name,
            "scheduled_time": str(task.scheduled_time),
            "goal_time": str(task.goal_time) if task.goal_time else None,
            "user_timezone": user_current_tz
        })

    return {
        "user_id": user_id,
        "current_timezone": user_current_tz,
        "tasks": adjusted_tasks
    } 