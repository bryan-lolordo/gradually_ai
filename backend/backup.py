import os
import redis
import re
import pytz
from openai import OpenAI
from datetime import datetime, time, date, timedelta
from tzlocal import get_localzone  
from typing import List, Union, Optional
from dotenv import load_dotenv

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import SessionLocal  # ✅ Centralized database connection
from models import User, BaselineSchedule, DailySchedule, Task, HabitAdjustment, ScheduleAdjustment
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# ✅ Load environment variables
load_dotenv()
client = OpenAI()

# Initialize FastAPI app
app = FastAPI()

# ✅ Redis Cache Setup
try:
    redis_client = redis.Redis(host="localhost", port=6379, db=0, socket_connect_timeout=5)
    FastAPICache.init(RedisBackend(redis_client), prefix="gradually_ai")
except redis.ConnectionError:
    print("❌ Redis connection failed. Caching is disabled.")
    redis_client = None

# ✅ Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define your request model above the endpoint function
class RegisterUserRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class BaselineTaskRequest(BaseModel):
    task_name: str
    scheduled_time: str  # "HH:MM:SS" format
    goal_time: Optional[str] = None  # Optional

class BaselineScheduleRequest(BaseModel):
    user_id: int
    tasks: List[BaselineTaskRequest]

# Define Pydantic model for request body
class TaskLogRequest(BaseModel):
    user_id: int
    task_name: str
    completed: bool
    scheduled_time: Optional[str] = None  # Expected format: "HH:MM:SS"
    goal_time: Optional[str] = None  # Optional goal time
    actual_completed_time: Optional[str] = None  # Expects "HH:MM:SS"
    log_date: Optional[str] = None  # Expects "YYYY-MM-DD"

class MultipleTaskLogRequest(BaseModel):
    tasks: list[TaskLogRequest]


class HabitUpdateRequest(BaseModel):
    habit: str  # ✅ Add the habit name
    status: str  # Either "accepted" or "rejected"

# Function to add the next day's scheduled tasks
def add_next_day_tasks():
    db = SessionLocal()
    tomorrow = (datetime.utcnow() + timedelta(days=1)).date()

    # Get all distinct user task schedules
    user_tasks = db.query(Task.user_id, Task.task_name, Task.scheduled_time, Task.goal_time).distinct().all()

    for user_id, task_name, scheduled_time, goal_time in user_tasks:
        existing_task = db.query(Task).filter(
            Task.user_id == user_id,
            Task.task_name == task_name,
            Task.log_date == tomorrow
        ).first()

        if not existing_task:
            new_task = Task(
                user_id=user_id,
                task_name=task_name,
                scheduled_time=scheduled_time,
                goal_time=goal_time,
                completed=False,
                log_date=tomorrow,
                created_at=datetime.utcnow()
            )
            db.add(new_task)

    db.commit()
    db.close()
    print(f"✅ Tasks added for {tomorrow}")

# Register User
@app.post("/users/register")
def register_user(request: RegisterUserRequest, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(request.password)
    new_user = User(username=request.username, email=request.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email}

# User Login
@app.post("/users/login")
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not pwd_context.verify(request.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    return {"user_id": user.id}

# Set Baseline Schedule
@app.post("/baseline_schedule/set")
def set_baseline_schedule(request: BaselineScheduleRequest, db: Session = Depends(get_db)):
    """Stores the user's baseline schedule with times converted to UTC."""
    
    user_id = request.user_id
    tasks = request.tasks  

    # ✅ Detect User's System Timezone
    user_current_tz = str(get_localzone())

    try:
        user_tz = pytz.timezone(user_current_tz)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid timezone detected.")

    # ✅ Delete old baseline schedule before inserting new tasks
    db.query(BaselineSchedule).filter(BaselineSchedule.user_id == user_id).delete()

    new_tasks = []
    for task in tasks:
        # ✅ Convert local scheduled time to UTC
        local_time = datetime.combine(datetime.today(), datetime.strptime(task.scheduled_time, "%H:%M:%S").time())

        if local_time.tzinfo is None:  # Ensure it's timezone-aware
            local_time = user_tz.localize(local_time)

        scheduled_time_utc = local_time.astimezone(pytz.utc).time()

        # ✅ Convert local goal time to UTC (if provided)
        goal_time_utc = None
        if task.goal_time:
            goal_time_local = datetime.combine(datetime.today(), datetime.strptime(task.goal_time, "%H:%M:%S").time())
            if goal_time_local.tzinfo is None:
                goal_time_local = user_tz.localize(goal_time_local)
            goal_time_utc = goal_time_local.astimezone(pytz.utc).time()

        new_task = BaselineSchedule(
            user_id=user_id,
            task_name=task.task_name,
            scheduled_time=scheduled_time_utc,
            goal_time=goal_time_utc,
            user_timezone=user_current_tz  # ✅ Store detected timezone
        )
        db.add(new_task)
        new_tasks.append(new_task)

    db.commit()

    return {
        "message": "Baseline schedule set successfully.",
        "detected_timezone": user_current_tz,
        "tasks": [{"task_name": t.task_name, "scheduled_time": str(t.scheduled_time), "goal_time": str(t.goal_time) if t.goal_time else None} for t in new_tasks]
    }

# Get Baseline Schedule
@app.get("/baseline_schedule/{user_id}")
def get_baseline_schedule(user_id: int, request: Request, db: Session = Depends(get_db)):
    """Fetches the user's baseline schedule and adjusts times to their current timezone."""

    tasks = db.query(BaselineSchedule).filter(BaselineSchedule.user_id == user_id).all()

    if not tasks:
        return {"message": "No baseline schedule found."}

    # ✅ Get User's Current Timezone from Request Headers (or use stored timezone)
    user_current_tz = request.headers.get("User-Timezone")
    if not user_current_tz:
        user_current_tz = tasks[0].user_timezone  # ✅ Fallback to stored timezone

    try:
        user_tz = pytz.timezone(user_current_tz)  # ✅ Validate timezone
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid timezone.")

    # ✅ Convert Scheduled & Goal Times from UTC → User's Timezone
    adjusted_tasks = []
    for task in tasks:
        scheduled_time_local = datetime.combine(datetime.today(), task.scheduled_time)\
            .replace(tzinfo=pytz.utc)\
            .astimezone(user_tz)\
            .time()

        goal_time_local = None
        if task.goal_time:
            goal_time_utc = datetime.combine(datetime.today(), task.goal_time).replace(tzinfo=pytz.utc)
            goal_time_local = goal_time_utc.astimezone(user_tz).time()

        adjusted_tasks.append({
            "task_name": task.task_name,
            "scheduled_time": str(scheduled_time_local),  # ✅ Now correctly converted
            "goal_time": str(goal_time_local) if goal_time_local else None,
            "user_timezone": user_current_tz
        })

    return {
        "user_id": user_id,
        "current_timezone": user_current_tz,
        "tasks": adjusted_tasks
    }

# Generate Daily Schedule
from models import ScheduleAdjustment  # Import the new model

@app.post("/daily_schedule/generate/{user_id}")
def generate_daily_schedule(user_id: int, db: Session = Depends(get_db), date_str: Optional[str] = None):
    """Generates a Daily Schedule for the specified date (defaults to today) with rule-based time adjustments."""
    
    user_current_tz = str(get_localzone())
    try:
        user_tz = pytz.timezone(user_current_tz)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid timezone detected.")

    target_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now(user_tz).date()
    existing_schedule = db.query(DailySchedule).filter(
        DailySchedule.user_id == user_id,
        DailySchedule.log_date == target_date
    ).first()

    if existing_schedule:
        return {"message": f"Daily schedule for {target_date} already exists. No changes were made."}

    past_days = target_date - timedelta(days=7)
    past_logs = db.query(DailySchedule).filter(
        DailySchedule.user_id == user_id,
        DailySchedule.log_date >= past_days,
        DailySchedule.status == "completed"
    ).all()
    
    task_actual_times = {}
    for task in past_logs:
        if task.task_name not in task_actual_times:
            task_actual_times[task.task_name] = []
        if task.actual_completed_time:
            task_actual_times[task.task_name].append(task.actual_completed_time.time())

    baseline_tasks = db.query(BaselineSchedule).filter(BaselineSchedule.user_id == user_id).all()
    
    for task in baseline_tasks:
        new_scheduled_time = task.scheduled_time
        previous_scheduled_time = None

        # ✅ Check if task exists in previous schedule & store old time
        last_scheduled_entry = db.query(DailySchedule).filter(
            DailySchedule.user_id == user_id,
            DailySchedule.task_name == task.task_name
        ).order_by(DailySchedule.log_date.desc()).first()

        if last_scheduled_entry:
            previous_scheduled_time = last_scheduled_entry.scheduled_time

        # ✅ Rule-Based Adjustment: Shift scheduled time toward goal time
        adjustment_reason = "No change"
        if task.task_name in task_actual_times and task.goal_time:
            past_actuals = [datetime.combine(datetime.today(), t) for t in task_actual_times[task.task_name]]
            if past_actuals:
                avg_actual_time = sum((t.hour * 60 + t.minute) for t in past_actuals) // len(past_actuals)
                avg_actual_time = timedelta(minutes=avg_actual_time)
                goal_time_delta = timedelta(hours=task.goal_time.hour, minutes=task.goal_time.minute)

                if avg_actual_time < goal_time_delta:
                    new_scheduled_time = (datetime.combine(datetime.today(), task.scheduled_time) - timedelta(minutes=5)).time()
                    adjustment_reason = "Shifted earlier toward goal time"
                elif avg_actual_time > goal_time_delta:
                    new_scheduled_time = (datetime.combine(datetime.today(), task.scheduled_time) + timedelta(minutes=5)).time()
                    adjustment_reason = "Shifted later based on completion trends"

        # ✅ Log adjustment if scheduled time changed
        if previous_scheduled_time and previous_scheduled_time != new_scheduled_time:
            adjustment_entry = ScheduleAdjustment(
                user_id=user_id,
                task_name=task.task_name,
                previous_scheduled_time=previous_scheduled_time,
                new_scheduled_time=new_scheduled_time,
                adjustment_reason=adjustment_reason,
                log_date=target_date
            )
            db.add(adjustment_entry)

        new_task = DailySchedule(
            user_id=user_id,
            task_name=task.task_name,
            scheduled_time=new_scheduled_time,
            previous_scheduled_time=previous_scheduled_time,  # ✅ Store old schedule time
            goal_time=task.goal_time,
            log_date=target_date,
            user_timezone=user_current_tz,
            status="pending"
        )
        db.add(new_task)
    
    db.commit()
    return {"message": f"Daily schedule for {target_date} generated successfully with rule-based adjustments."}



# ✅ Background Job: Run Daily Schedule Generation at Midnight
def schedule_daily_generation():
    """Automates next-day schedule generation at midnight UTC."""
    db = SessionLocal()
    users = db.query(User.id).all()

    for user in users:
        user_id = user.id

        # ✅ Detect User's Timezone
        user_tz = db.query(BaselineSchedule.user_timezone).filter(BaselineSchedule.user_id == user_id).scalar()
        if not user_tz:
            user_tz = "UTC"  # Default to UTC if no timezone is found
        user_tz = pytz.timezone(user_tz)

        # ✅ Get the next day's date in the user's timezone
        next_day = datetime.now(user_tz).date() + timedelta(days=1)

        # ✅ Clear only planned tasks (keep ad-hoc)
        db.query(DailySchedule).filter(
            DailySchedule.user_id == user_id, 
            DailySchedule.log_date == next_day,
            DailySchedule.scheduled_time.isnot(None)  # ✅ Ensures ad-hoc tasks are not deleted
        ).delete()

        # ✅ Copy from baseline schedule
        baseline_tasks = db.query(BaselineSchedule).filter(BaselineSchedule.user_id == user_id).all()

        for task in baseline_tasks:
            new_task = DailySchedule(
                user_id=user_id,
                task_name=task.task_name,
                scheduled_time=task.scheduled_time,
                goal_time=task.goal_time,
                log_date=next_day,
                user_timezone=user_tz.zone,
                status="pending"
            )
            db.add(new_task)

    db.commit()
    db.close()
    print(f"✅ Next-day schedule generated at midnight UTC.")

# ✅ Scheduler: Run `schedule_daily_generation` at 12:00 AM UTC
scheduler = BackgroundScheduler()
scheduler.add_job(schedule_daily_generation, "cron", hour=0, minute=0)  # Runs at midnight UTC
scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    """Shutdown the scheduler when FastAPI stops."""
    scheduler.shutdown()

# Get Daily Schedule
@app.get("/daily_schedule/{user_id}")
def get_daily_schedule(user_id: int, request: Request, db: Session = Depends(get_db)):
    """Fetches all tasks (planned & ad-hoc) for the user's daily schedule."""

    # ✅ Detect User's System Timezone
    user_current_tz = request.headers.get("User-Timezone") or str(get_localzone())

    try:
        user_tz = pytz.timezone(user_current_tz)  
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid timezone.")

    # ✅ Get current date in UTC
    today_utc = datetime.now(pytz.utc).date()

    # ✅ Retrieve all daily schedule tasks for the user
    daily_tasks = db.query(DailySchedule).filter(
        DailySchedule.user_id == user_id,
        DailySchedule.log_date == today_utc
    ).all()

    if not daily_tasks:
        return {"message": "No daily schedule found for today. Try generating it first."}

    adjusted_schedule = []

    for task in daily_tasks:
        try:
            # ✅ Convert scheduled & goal times from UTC to the user's timezone
            scheduled_time_local = None
            if task.scheduled_time:
                scheduled_time_local = datetime.combine(today_utc, task.scheduled_time)\
                    .replace(tzinfo=pytz.utc)\
                    .astimezone(user_tz)\
                    .time()

            goal_time_local = None
            if task.goal_time:
                goal_time_local = datetime.combine(today_utc, task.goal_time)\
                    .replace(tzinfo=pytz.utc)\
                    .astimezone(user_tz)\
                    .time()

            adjusted_schedule.append({
                "task_name": task.task_name,
                "scheduled_time": scheduled_time_local.strftime("%H:%M:%S") if scheduled_time_local else None,  
                "goal_time": goal_time_local.strftime("%H:%M:%S") if goal_time_local else None,
                "status": task.status
            })
        except Exception as e:
            print(f"❌ Error converting {task.task_name}: {str(e)}")

    return {
        "user_id": user_id,
        "log_date": str(today_utc),
        "current_timezone": user_current_tz,
        "schedule": adjusted_schedule
    }

# ✅ Task Logging API
@app.post("/tasks/log")
def log_tasks(request: MultipleTaskLogRequest, db: Session = Depends(get_db)):
    """Logs task completion. If the task isn't in daily_schedules, it is added as an ad-hoc task."""

    updated_tasks = []
    user_current_tz = str(get_localzone())

    try:
        user_tz = pytz.timezone(user_current_tz)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid timezone detected.")

    today_utc = datetime.now(pytz.utc).date()

    for task_data in request.tasks:
        log_date = datetime.strptime(task_data.log_date, "%Y-%m-%d").date() if task_data.log_date else today_utc

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
            db.commit()

        if task_data.actual_completed_time:
            local_datetime = user_tz.localize(datetime.combine(log_date, datetime.strptime(task_data.actual_completed_time, "%H:%M:%S").time()))
            utc_time = local_datetime.astimezone(pytz.utc)
        else:
            utc_time = datetime.now(pytz.utc)

        task.status = "completed" if task_data.completed else "pending"
        task.actual_completed_time = utc_time

        db.commit()
        updated_tasks.append({
            "task_name": task.task_name,
            "log_date": str(log_date),
            "status": task.status,
            "actual_completed_time": str(utc_time.time()) if task.actual_completed_time else None
        })

    return {"message": "Tasks logged successfully", "tasks": updated_tasks}

# Parse AI Suggestion
def parse_ai_suggestion(suggestion: str):
    """Extracts habit, suggested time, and reason from AI response."""
    
    # ✅ Ensure valid structure: "Habit Name: Suggested Time - Reason"
    pattern = r"^(.*?):\s*(\d{1,2}:\d{2}:\d{2})\s*-\s*(.*)$"
    match = re.match(pattern, suggestion.strip())

    if match:
        habit = match.group(1).strip()
        suggested_value = match.group(2).strip()
        reason = match.group(3).strip()
        return habit, suggested_value, reason

    # 🚨 If AI response is invalid, return None
    return None, None, suggestion

# AI Habit Adjustments
@app.get("/ai/habit_adjustments/{user_id}")
def generate_ai_habit_adjustments(user_id: int, db: Session = Depends(get_db)):
    """Uses AI to analyze a user's daily schedule & suggest habit improvements."""

    # ✅ Fetch today's completed tasks from `daily_schedules`
    today_utc = datetime.now(pytz.utc).date()
    tasks = db.query(DailySchedule).filter(
        DailySchedule.user_id == user_id,
        DailySchedule.log_date == today_utc
    ).all()

    if not tasks:
        return {"message": "No tasks found for this user."}

    # ✅ Prepare habit data for AI
    habit_data = []
    for task in tasks:
        habit_data.append({
            "habit": task.task_name,
            "scheduled_time": str(task.scheduled_time) if task.scheduled_time else None,
            "goal_time": str(task.goal_time) if task.goal_time else None,
            "actual_completed_time": str(task.actual_completed_time.time()) if task.actual_completed_time else None,
            "status": task.status
        })

    # ✅ Ask GPT-4 for habit improvement suggestions
    response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a habit improvement coach."},
        {"role": "user", "content": f"Here is my current habit schedule: {habit_data}. How should I adjust to better reach my goal times?"}
        ]
    )
    ai_suggestions = response.choices[0].message.content

    # ✅ Store AI-generated habit adjustments
    adjustments = []
    for suggestion in ai_suggestions.split("\n"):
        if suggestion.strip():
            habit, suggested_value, reason = parse_ai_suggestion(suggestion)

            # ✅ Find the current scheduled time for this habit
            current_value = db.query(DailySchedule.scheduled_time).filter(
                DailySchedule.user_id == user_id,
                DailySchedule.task_name == habit,
                DailySchedule.log_date == today_utc
            ).scalar()

            # ✅ Check if habit, suggested_value, and reason are valid
            if habit and suggested_value and reason:
                adjustment = HabitAdjustment(
                    user_id=user_id,
                    habit=habit,
                    current_value=current_value,
                    suggested_value=suggested_value,
                    reason=reason,
                    status="pending",
                    log_date=today_utc
                )
                db.add(adjustment)
                adjustments.append({
                    "habit": habit,
                    "suggested_value": suggested_value,
                    "reason": reason
                })
            else:
                print(f"❌ Skipping invalid adjustment: {habit}, {suggested_value}, {reason}")

    db.commit()
    return {"ai_recommendations": adjustments}

# Get Schedule Adjustments
@app.get("/schedule_adjustments/{user_id}")
def get_schedule_adjustments(user_id: int, db: Session = Depends(get_db)):
    """Fetches all schedule adjustments for a user."""

    adjustments = db.query(ScheduleAdjustment).filter(
        ScheduleAdjustment.user_id == user_id
    ).order_by(ScheduleAdjustment.log_date.desc()).all()

    if not adjustments:
        return {"message": "No schedule adjustments found."}

    return {
        "user_id": user_id,
        "adjustments": [
            {
                "task_name": adj.task_name,
                "previous_scheduled_time": str(adj.previous_scheduled_time),
                "new_scheduled_time": str(adj.new_scheduled_time),
                "adjustment_reason": adj.adjustment_reason,
                "log_date": str(adj.log_date)
            }
            for adj in adjustments
        ]
    }

# Respond to Habit Adjustments
@app.post("/ai/habit_adjustments/respond/{user_id}")
def respond_to_habit_adjustment(user_id: int, request: HabitUpdateRequest, db: Session = Depends(get_db)):
    """Accepts or rejects AI-suggested habit adjustments."""

    adjustment = db.query(HabitAdjustment).filter(
        HabitAdjustment.user_id == user_id,
        HabitAdjustment.habit == request.habit,
        HabitAdjustment.status == "pending"
    ).first()

    if not adjustment:
        return {"message": "No pending adjustment found for this habit."}

    # ✅ Update status
    if request.status == "accepted":
        adjustment.status = "accepted"

        # ✅ Update `daily_schedules` to reflect the accepted change
        db.query(DailySchedule).filter(
            DailySchedule.user_id == user_id,
            DailySchedule.task_name == request.habit,
            DailySchedule.log_date == adjustment.log_date
        ).update({"scheduled_time": adjustment.suggested_value})

    elif request.status == "rejected":
        adjustment.status = "rejected"

    db.commit()
    return {"message": f"Habit adjustment for {request.habit} marked as {request.status}."}


# ✅ Health Check Endpoint
@app.get("/")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")  # ✅ Run a simple database check
        return {"message": "API is running!"}
    except Exception as e:
        return {"message": "Database connection error", "error": str(e)}

# ✅ Initialize Tables
def init_db():
    from database import engine
    print("🔄 Checking database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
