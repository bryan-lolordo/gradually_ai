import requests
import random
from datetime import datetime, timedelta
import json

# FastAPI endpoint for logging tasks
API_URL = "http://127.0.0.1:8000/tasks/log"

# **Fixed Schedule & Goal Times (No Randomization)**
tasks = [
    {"task_name": "Wake Up", "scheduled_time": "08:30:00", "goal_time": "07:30:00"},
    {"task_name": "Get Out of Bed", "scheduled_time": "09:30:00", "goal_time": "08:15:00"},
    {"task_name": "Breakfast", "scheduled_time": "10:00:00", "goal_time": "08:45:00"},
    {"task_name": "Lunch", "scheduled_time": "14:00:00", "goal_time": "12:30:00"},
    {"task_name": "Gym", "scheduled_time": "15:15:00", "goal_time": "14:00:00"},
    {"task_name": "Coffee", "scheduled_time": "17:00:00", "goal_time": "15:30:00"},
    {"task_name": "Dinner", "scheduled_time": "18:30:00", "goal_time": "17:00:00"},
    {"task_name": "Shower", "scheduled_time": "18:00:00", "goal_time": "15:45:00"},
    {"task_name": "Sleep", "scheduled_time": "02:00:00", "goal_time": "23:30:00"},
]

# **Generate historical logs for the past 7 days**
historical_data = []
start_date = datetime.utcnow() - timedelta(days=7)

for i in range(7):  # Generate logs for the past 7 days
    log_date = (start_date + timedelta(days=i)).date()  # ✅ Correct past date

    for task in tasks:
        # ✅ **Randomize actual log time within ±15 minutes of scheduled time**
        scheduled_dt = datetime.strptime(task["scheduled_time"], "%H:%M:%S")
        random_offset = random.randint(-15, 15) * 60  # Randomize within ±15 minutes
        actual_completed_dt = scheduled_dt + timedelta(seconds=random_offset)

        historical_data.append({
            "user_id": 1,
            "task_name": task["task_name"],
            "completed": True,
            "actual_completed_time": actual_completed_dt.strftime("%H:%M:%S"),
            "log_date": log_date.strftime("%Y-%m-%d")  # ✅ Ensure correct date is sent
        })

# **Check output before sending**
print(json.dumps({"tasks": historical_data}, indent=4))

# **Send request to API**
response = requests.post(API_URL, json={"tasks": historical_data})

# **Check API response**
print("Status Code:", response.status_code)
print("Response:", response.json())

