from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class TaskLogRequest(BaseModel):
    user_id: int
    task_name: str
    completed: bool
    scheduled_time: Optional[str] = None
    goal_time: Optional[str] = None
    actual_completed_time: Optional[str] = None
    log_date: Optional[str] = None

class MultipleTaskLogRequest(BaseModel):
    tasks: List[TaskLogRequest]

class TaskResponse(BaseModel):
    task_name: str
    scheduled_time: Optional[str]
    goal_time: Optional[str]
    actual_completed_time: Optional[str]
    completed: bool
    ad_hoc: bool 