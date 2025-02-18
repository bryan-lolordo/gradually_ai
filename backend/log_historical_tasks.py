import requests
from datetime import datetime, timedelta
import json

# FastAPI endpoint for adding tasks
API_URL = "http://127.0.0.1:8000/tasks/add"

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

# **Generate historical data for past 7 days**
historical_data = []
start_date = datetime.utcnow() - timedelta(days=7)

for i in range(7):  # Generate logs for the past 7 days
    log_date = (start_date + timedelta(days=i)).date()  # ✅ Correct past date

    for task in tasks:
        historical_data.append({
            "user_id": 1,
            "task_name": task["task_name"],
            "scheduled_time": task["scheduled_time"],  # ✅ Fixed scheduled time
            "goal_time": task["goal_time"],  # ✅ Fixed goal time
        })

# **Check output before sending**
print(json.dumps({"tasks": historical_data}, indent=4))

# **Send request to API**
response = requests.post(API_URL, json={"tasks": historical_data})

# **Check API response**
print("Status Code:", response.status_code)
print("Response:", response.json())

