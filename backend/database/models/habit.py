from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Time, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .. import Base

class HabitAdjustment(Base):
    __tablename__ = "habit_adjustments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    habit = Column(String, nullable=False)
    log_date = Column(Date, nullable=False)  # Tracks which day this adjustment is for
    current_value = Column(Time, nullable=False)  # Matches `daily_schedules`
    suggested_value = Column(Time, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, accepted, rejected
    current_status = Column(String, default="pending")  # Matches `daily_schedules.status`
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="habit_adjustments")

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