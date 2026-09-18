from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from database import get_db_context
from database.models import User, DailySchedule, HabitAdjustment
from utils import TimeUtils

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Request Models (will move to schemas later)
from pydantic import BaseModel

class HabitUpdateRequest(BaseModel):
    habit: str
    status: str

@router.get("/adjustments/{user_id}")
def get_habit_adjustments(user_id: int, db: Session = Depends(get_db_context)):
    """Get all pending habit adjustments for a user."""
    
    adjustments = db.query(HabitAdjustment).filter(
        HabitAdjustment.user_id == user_id,
        HabitAdjustment.status == "pending"
    ).all()

    return {
        "adjustments": [{
            "habit": adj.habit,
            "current_value": str(adj.current_value),
            "suggested_value": str(adj.suggested_value),
            "reason": adj.reason,
            "status": adj.status
        } for adj in adjustments]
    }

@router.post("/adjustments/{adjustment_id}/update")
def update_habit_adjustment(
    adjustment_id: int,
    request: HabitUpdateRequest,
    db: Session = Depends(get_db_context)
):
    """Update the status of a habit adjustment."""
    
    adjustment = db.query(HabitAdjustment).filter(
        HabitAdjustment.id == adjustment_id
    ).first()

    if not adjustment:
        raise HTTPException(status_code=404, detail="Adjustment not found")

    try:
        adjustment.status = request.status
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating adjustment {adjustment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update adjustment")

    return {"message": "Adjustment updated successfully"}

@router.get("/analysis/{user_id}")
def analyze_habits(user_id: int, db: Session = Depends(get_db_context)):
    """Analyze user's habits and provide insights."""
    
    # Get user's timezone
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_time = TimeUtils.get_current_time(user.timezone)
    today = current_time.date()

    # Get completed tasks for analysis
    completed_tasks = db.query(DailySchedule).filter(
        DailySchedule.user_id == user_id,
        DailySchedule.status == "completed",
        DailySchedule.actual_completed_time.isnot(None)
    ).all()

    # Analyze completion patterns
    task_patterns = {}
    for task in completed_tasks:
        if task.task_name not in task_patterns:
            task_patterns[task.task_name] = {
                "total_completions": 0,
                "on_time_completions": 0,
                "average_delay": 0
            }

        pattern = task_patterns[task.task_name]
        pattern["total_completions"] += 1

        if task.scheduled_time and task.actual_completed_time:
            scheduled_datetime = datetime.combine(task.log_date, task.scheduled_time)
            actual_datetime = task.actual_completed_time
            
            # Convert to user's timezone for comparison
            scheduled_local = TimeUtils.convert_timezone(scheduled_datetime, user.timezone)
            actual_local = TimeUtils.convert_timezone(actual_datetime, user.timezone)
            
            delay = (actual_local - scheduled_local).total_seconds() / 60  # in minutes
            pattern["average_delay"] = (pattern["average_delay"] * (pattern["total_completions"] - 1) + delay) / pattern["total_completions"]
            
            if delay <= 15:  # Consider within 15 minutes as "on time"
                pattern["on_time_completions"] += 1

    # Generate insights
    insights = []
    for task_name, pattern in task_patterns.items():
        if pattern["total_completions"] >= 5:  # Only analyze tasks with enough data
            completion_rate = pattern["on_time_completions"] / pattern["total_completions"] * 100
            avg_delay = pattern["average_delay"]

            if completion_rate >= 80:
                insights.append({
                    "task": task_name,
                    "type": "positive",
                    "message": f"Great job! You complete {task_name} on time {completion_rate:.1f}% of the time."
                })
            elif completion_rate <= 30:
                insights.append({
                    "task": task_name,
                    "type": "suggestion",
                    "message": f"Consider adjusting the schedule for {task_name}. You're often {avg_delay:.0f} minutes late."
                })

    return {
        "task_patterns": task_patterns,
        "insights": insights
    } 