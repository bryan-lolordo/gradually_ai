from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from tzlocal import get_localzone
import logging

from database import get_db_context
from database.models import User, Task, DailySchedule
from utils import TimeUtils

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Request Models (will move to schemas later)
from pydantic import BaseModel

class TaskLogRequest(BaseModel):
    user_id: int
    task_name: str
    completed: bool
    scheduled_time: Optional[str] = None
    goal_time: Optional[str] = None
    actual_completed_time: Optional[str] = None
    log_date: Optional[str] = None

class MultipleTaskLogRequest(BaseModel):
    tasks: List[TaskLogRequest]

@router.post("/log")
def log_tasks(request: MultipleTaskLogRequest, db: Session = Depends(get_db_context)):
    """Logs task completion and ensures actual_completed_time is stored in UTC."""

    updated_tasks = []
    user_current_tz = str(get_localzone())

    if not TimeUtils.validate_timezone(user_current_tz):
        raise HTTPException(status_code=400, detail="Invalid timezone detected.")

    current_time = TimeUtils.get_current_time(user_current_tz)
    today_utc = current_time.date()

    for task_data in request.tasks:
        try:
            # Ensure log_date is valid
            log_date = datetime.strptime(task_data.log_date, "%Y-%m-%d").date() if task_data.log_date else today_utc

            # Fetch or create task entry
            task = db.query(DailySchedule).filter(
                DailySchedule.user_id == task_data.user_id,
                DailySchedule.task_name == task_data.task_name,
                DailySchedule.log_date == log_date
            ).first()

            if not task:
                task = DailySchedule(
                    user_id=task_data.user_id,
                    task_name=task_data.task_name,
                    log_date=log_date,
                    user_timezone=user_current_tz,
                    status="pending"
                )
                db.add(task)

            # Parse completion time
            if task_data.actual_completed_time:
                try:
                    completion_time = TimeUtils.parse_time_string(task_data.actual_completed_time)
                    task.actual_completed_time = datetime.combine(log_date, completion_time)
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid time format for task {task_data.task_name}")
            else:
                task.actual_completed_time = current_time

            # Update task status
            task.status = "completed" if task_data.completed else "pending"
            updated_tasks.append(task)

        except Exception as e:
            logger.error(f"Error processing task {task_data.task_name}: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to log task {task_data.task_name}")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save task logs")

    return {
        "message": "Tasks logged successfully",
        "updated_tasks": [{"task_name": t.task_name, "status": t.status} for t in updated_tasks]
    }

@router.get("/{user_id}")
def get_user_tasks(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db_context),
    date_str: Optional[str] = None
):
    """Get all tasks for a user on a specific date."""
    
    user_current_tz = request.headers.get("User-Timezone", str(get_localzone()))
    if not TimeUtils.validate_timezone(user_current_tz):
        raise HTTPException(status_code=400, detail="Invalid timezone.")

    current_time = TimeUtils.get_current_time(user_current_tz)
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else current_time.date()

    tasks = db.query(Task).filter(
        Task.user_id == user_id,
        Task.log_date == target_date
    ).all()

    return {
        "user_id": user_id,
        "log_date": str(target_date),
        "current_timezone": user_current_tz,
        "tasks": [{
            "task_name": task.task_name,
            "scheduled_time": str(task.scheduled_time) if task.scheduled_time else None,
            "goal_time": str(task.goal_time) if task.goal_time else None,
            "actual_completed_time": str(task.actual_completed_time) if task.actual_completed_time else None,
            "completed": task.completed,
            "ad_hoc": task.ad_hoc
        } for task in tasks]
    } 