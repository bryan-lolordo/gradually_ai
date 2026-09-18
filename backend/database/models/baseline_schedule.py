from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Time
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .. import Base

class BaselineSchedule(Base):
    __tablename__ = "baseline_schedule"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    task_name = Column(String)
    scheduled_time = Column(Time)
    goal_time = Column(Time, nullable=True)
    user_timezone = Column(String, default="UTC")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="baseline_schedule") 