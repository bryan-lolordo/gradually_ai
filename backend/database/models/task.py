from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Time, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .. import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_name = Column(String, nullable=False)
    scheduled_time = Column(Time, nullable=True)  # From the daily schedule
    goal_time = Column(Time, nullable=True)  # What user wants to aim for
    actual_completed_time = Column(DateTime, nullable=True)  # When user actually did it
    log_date = Column(Date, nullable=False)  # The date user logged this
    ad_hoc = Column(Boolean, default=False)  # If this was not originally scheduled
    completed = Column(Boolean, default=False)  # Did user complete it?
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="tasks") 