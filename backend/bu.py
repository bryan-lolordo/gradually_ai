import os
import redis
import re
import pytz
import jwt
from openai import OpenAI
from datetime import datetime, timedelta
from tzlocal import get_localzone  
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from apscheduler.schedulers.background import BackgroundScheduler

from database import SessionLocal
from models import User, BaselineSchedule, DailySchedule, Task, HabitAdjustment, ScheduleAdjustment

# ✅ Load environment variables securely
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
client = OpenAI()

# ✅ Initialize FastAPI
app = FastAPI()

# ✅ Redis Cache Setup
try:
    redis_client = redis.Redis(host="localhost", port=6379, db=0, socket_connect_timeout=5)
    FastAPICache.init(RedisBackend(redis_client), prefix="gradually_ai")
except redis.ConnectionError:
    print("❌ Redis connection failed. Caching is disabled.")
    redis_client = None

# ✅ Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ JWT Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ✅ Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"❌ Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# ✅ Helper Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Extracts and validates user from JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=403, detail="Invalid token")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

# ✅ Register User
@app.post("/users/register")
def register_user(username: str, email: str, password: str, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(password)
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email}

# ✅ User Login
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

# ✅ Set Baseline Schedule
@app.post("/baseline_schedule/set")
def set_baseline_schedule(tasks: List[dict], db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Stores the user's baseline schedule with UTC conversion."""
    user_current_tz = str(get_localzone())

    db.query(BaselineSchedule).filter(BaselineSchedule.user_id == user.id).delete()

    for task in tasks:
        local_time = datetime.strptime(task["scheduled_time"], "%H:%M:%S").time()
        goal_time = datetime.strptime(task["goal_time"], "%H:%M:%S").time() if task.get("goal_time") else None
        scheduled_time_utc = pytz.timezone(user_current_tz).localize(datetime.combine(datetime.today(), local_time)).astimezone(pytz.utc).time()

        new_task = BaselineSchedule(
            user_id=user.id,
            task_name=task["task_name"],
            scheduled_time=scheduled_time_utc,
            goal_time=goal_time,
            user_timezone=user_current_tz
        )
        db.add(new_task)

    db.commit()
    return {"message": "Baseline schedule set successfully", "detected_timezone": user_current_tz}

# ✅ Get Tasks (Paginated)
@app.get("/tasks/")
def get_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Fetches paginated user tasks."""
    return db.query(Task).filter(Task.user_id == user.id).offset(skip).limit(limit).all()

# ✅ AI Habit Adjustments
@app.get("/ai/habit_adjustments")
def generate_ai_habit_adjustments(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Uses AI to suggest habit improvements based on past schedules."""
    today_utc = datetime.now(pytz.utc).date()
    tasks = db.query(DailySchedule).filter(DailySchedule.user_id == user.id, DailySchedule.log_date == today_utc).all()
    
    if not tasks:
        return {"message": "No tasks found for this user."}

    habit_data = [{"habit": t.task_name, "scheduled_time": str(t.scheduled_time), "status": t.status} for t in tasks]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a habit improvement coach."},
            {"role": "user", "content": f"Here is my current habit schedule: {habit_data}. Suggest improvements."}
        ]
    )
    ai_suggestions = response.choices[0].message.content

    return {"ai_recommendations": ai_suggestions}

# ✅ Health Check Endpoint
@app.get("/")
def health_check():
    return {"message": "API is running!"}

# ✅ Background Job for Next-Day Schedule
def schedule_daily_generation():
    """Automates next-day schedule generation."""
    db = SessionLocal()
    users = db.query(User.id).all()

    for user in users:
        user_id = user.id
        user_tz = db.query(BaselineSchedule.user_timezone).filter(BaselineSchedule.user_id == user_id).scalar() or "UTC"
        next_day = datetime.now(pytz.timezone(user_tz)).date() + timedelta(days=1)

        db.query(DailySchedule).filter(DailySchedule.user_id == user_id, DailySchedule.log_date == next_day).delete()
        baseline_tasks = db.query(BaselineSchedule).filter(BaselineSchedule.user_id == user_id).all()

        for task in baseline_tasks:
            db.add(DailySchedule(user_id=user_id, task_name=task.task_name, scheduled_time=task.scheduled_time, log_date=next_day, status="pending"))

    db.commit()
    db.close()

# ✅ Run at Midnight UTC
scheduler = BackgroundScheduler()
scheduler.add_job(schedule_daily_generation, "cron", hour=0, minute=0)
scheduler.start()
