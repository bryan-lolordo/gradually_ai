from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HabitUpdateRequest(BaseModel):
    habit: str
    status: str

class HabitAdjustmentResponse(BaseModel):
    habit: str
    current_value: str
    suggested_value: str
    reason: str
    status: str

class ScheduleAdjustmentResponse(BaseModel):
    task_name: str
    previous_scheduled_time: Optional[str]
    new_scheduled_time: str
    adjustment_reason: str
    log_date: datetime 