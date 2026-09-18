from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import logging

from database import get_db_context
from database.models import User, DailySchedule, BaselineSchedule
from utils import TimeUtils

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.post("/generate/{user_id}")
def generate_daily_schedule(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db_context),
    date_str: Optional[str] = None,
    auto: bool = False
):
    """Generates a Daily Schedule dynamically with rule-based time adjustments."""

    if not auto and not user_id:
        raise HTTPException(status_code=400, detail="User ID is required for manual schedule generation.")

    users = db.query(User.id).all() if auto else [(user_id,)]

    for user_tuple in users:
        user_id = user_tuple[0]

        # Get User's Timezone
        user_tz = db.query(BaselineSchedule.user_timezone).filter(
            BaselineSchedule.user_id == user_id
        ).distinct().first()
        
        if not user_tz:
            continue

        user_tz = user_tz[0]
        if not TimeUtils.validate_timezone(user_tz):
            logger.error(f"Invalid timezone {user_tz} for user {user_id}")
            continue

        # Set target date
        current_time = TimeUtils.get_current_time(user_tz)
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else current_time.date()

        # Skip if schedule exists
        if db.query(DailySchedule).filter(
            DailySchedule.user_id == user_id,
            DailySchedule.log_date == target_date
        ).first():
            continue

        try:
            # Generate schedule from baseline
            baseline_tasks = db.query(BaselineSchedule).filter(BaselineSchedule.user_id == user_id).all()
            
            for task in baseline_tasks:
                new_scheduled_time = task.scheduled_time
                previous_scheduled_time = None

                # Get last scheduled time
                last_scheduled = db.query(DailySchedule).filter(
                    DailySchedule.user_id == user_id,
                    DailySchedule.task_name == task.task_name
                ).order_by(DailySchedule.log_date.desc()).first()

                if last_scheduled:
                    previous_scheduled_time = last_scheduled.scheduled_time

                # Create daily schedule entry
                db.add(DailySchedule(
                    user_id=user_id,
                    task_name=task.task_name,
                    scheduled_time=new_scheduled_time,
                    previous_scheduled_time=previous_scheduled_time,
                    goal_time=task.goal_time,
                    log_date=target_date,
                    user_timezone=user_tz,
                    status="pending"
                ))

            db.commit()

        except Exception as e:
            db.rollback()
            logger.error(f"Error generating schedule for user {user_id}: {str(e)}")
            if not auto:
                raise HTTPException(status_code=500, detail="Failed to generate daily schedule")

    return {"message": f"Daily schedule for {target_date} generated successfully."} 