from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class BaselineTaskRequest(BaseModel):
    task_name: str
    scheduled_time: str
    goal_time: Optional[str] = None

class BaselineScheduleRequest(BaseModel):
    user_id: int
    tasks: List[BaselineTaskRequest]

class BaselineScheduleResponse(BaseModel):
    task_name: str
    scheduled_time: str
    goal_time: Optional[str]
    user_timezone: str

class DailyScheduleRequest(BaseModel):
    user_id: Optional[int]
    date: Optional[date]
    auto: bool = False

class DailyScheduleResponse(BaseModel):
    task_name: str
    scheduled_time: str
    previous_scheduled_time: Optional[str]
    goal_time: Optional[str]
    status: str
    actual_completed_time: Optional[str] 