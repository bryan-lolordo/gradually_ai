from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON, Float, Time, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, time, date, timezone
from database import Base, engine  # Importing Base and engine from database.py
import pytz

# User Table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    timezone = Column(String, default="UTC")  # ✅ Store user timezone
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # ✅ UTC-aware timestamp

# Baseline Schedule
class BaselineSchedule(Base):
    __tablename__ = "baseline_schedule"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_name = Column(String, nullable=False)
    scheduled_time = Column(Time, nullable=False)  # ✅ Stored in UTC
    goal_time = Column(Time, nullable=True)  # ✅ Stored in UTC
    user_timezone = Column(String, nullable=False)  # ✅ Store user's timezone at the time of input
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="baseline_schedule")  # ✅ This makes the relationship bi-directional

# Daily Schedule Table
class DailySchedule(Base):
    __tablename__ = "daily_schedules"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_name = Column(String, nullable=False)
    scheduled_time = Column(Time, nullable=True)
    previous_scheduled_time = Column(Time, nullable=True)  # ✅ NEW COLUMN
    goal_time = Column(Time, nullable=True)
    log_date = Column(Date, nullable=False)
    status = Column(String, default="pending")
    user_timezone = Column(String, nullable=False)
    actual_completed_time = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="daily_schedules")

# Tasks Table
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_name = Column(String, nullable=False)
    scheduled_time = Column(Time, nullable=True)  # ✅ From the daily schedule
    goal_time = Column(Time, nullable=True)  # ✅ What user wants to aim for
    actual_completed_time = Column(DateTime(timezone=True), nullable=True)  # ✅ When user actually did it
    log_date = Column(Date, nullable=False)  # ✅ The date user logged this
    ad_hoc = Column(Boolean, default=False)  # ✅ If this was not originally scheduled
    completed = Column(Boolean, default=False)  # ✅ Did user complete it?
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user = relationship("User", back_populates="tasks")


# AI Habit Adjustments 
class HabitAdjustment(Base):
    __tablename__ = "habit_adjustments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    habit = Column(String, nullable=False)
    log_date = Column(Date, nullable=False)  # ✅ Tracks which day this adjustment is for
    current_value = Column(Time, nullable=False)  # ✅ Matches `daily_schedules`
    suggested_value = Column(Time, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, accepted, rejected
    current_status = Column(String, default="pending")  # ✅ Matches `daily_schedules.status`
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user = relationship("User", back_populates="habit_adjustments")

# Schedule Adjustments
class ScheduleAdjustment(Base):
    __tablename__ = "schedule_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_name = Column(String, nullable=False)
    previous_scheduled_time = Column(Time, nullable=True)  
    new_scheduled_time = Column(Time, nullable=False)  
    adjustment_reason = Column(String, nullable=False)
    log_date = Column(DateTime, nullable=False)  
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user = relationship("User", back_populates="schedule_adjustments")

# ✅ Add relationships in User model
User.baseline_schedule = relationship("BaselineSchedule", back_populates="user", cascade="all, delete-orphan")
User.daily_schedules = relationship("DailySchedule", back_populates="user", cascade="all, delete-orphan")
User.tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
User.habit_adjustments = relationship("HabitAdjustment", back_populates="user", cascade="all, delete-orphan")  # ✅ Use `HabitAdjustment`
User.schedule_adjustments = relationship("ScheduleAdjustment", back_populates="user", cascade="all, delete-orphan")


# Function to create tables
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("✅ Database tables created successfully!")
