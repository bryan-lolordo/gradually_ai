from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Time, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .. import Base

class DailySchedule(Base):
    __tablename__ = "daily_schedule"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_name = Column(String, nullable=False)
    scheduled_time = Column(Time, nullable=True)
    previous_scheduled_time = Column(Time, nullable=True)
    goal_time = Column(Time, nullable=True)
    log_date = Column(Date, nullable=False)
    status = Column(String, default="pending")
    user_timezone = Column(String, default="UTC")
    actual_completed_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="daily_schedules") 