from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .. import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    timezone = Column(String, default="UTC")  # Store user timezone
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # UTC-aware timestamp
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Define relationships using string names to avoid circular imports
    baseline_schedule = relationship("BaselineSchedule", back_populates="user", uselist=False, cascade="all, delete-orphan")
    daily_schedules = relationship("DailySchedule", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    habit_adjustments = relationship("HabitAdjustment", back_populates="user", cascade="all, delete-orphan")
    schedule_adjustments = relationship("ScheduleAdjustment", back_populates="user", cascade="all, delete-orphan") 