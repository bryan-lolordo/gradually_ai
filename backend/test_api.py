import requests
import json
from datetime import datetime, timedelta
import logging
import socket
import time
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import redis

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API Base URL
BASE_URL = "http://localhost:8000"  # Adjust if your server runs on a different port

def check_server_availability(host="localhost", port=8000, timeout=1):
    """Check if the server is running and port is accessible"""
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except (socket.timeout, socket.gaierror, ConnectionRefusedError):
        return False

def test_health_check(max_retries=3, retry_delay=2):
    """Test the health check endpoint with retries"""
    logger.info("🔄 Testing API health check...")

    # First check if server is available
    if not check_server_availability():
        logger.error("❌ Server is not running or port 8000 is not accessible")
        logger.info("Please ensure:")
        logger.info("1. FastAPI server is running")
        logger.info("2. Server is running on port 8000")
        logger.info("3. No firewall is blocking the connection")
        logger.info("4. Try running: uvicorn api:app --reload")
        return False

    for attempt in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/")
            if response.status_code == 200:
                logger.info("✅ Health check passed")
                logger.info(f"Response: {response.json()}")
                return True
            else:
                logger.warning(f"⚠️ Health check returned status code {response.status_code}")
                logger.info(f"Response: {response.text}")
        except requests.exceptions.ConnectionError:
            logger.warning(f"⚠️ Connection error on attempt {attempt + 1}/{max_retries}")
        except Exception as e:
            logger.error(f"❌ Health check failed with error: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
        
        if attempt < max_retries - 1:
            logger.info(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    logger.error("❌ Health check failed after all retries")
    return False

def test_user_registration():
    """Test user registration endpoint with detailed error handling"""
    logger.info("🔄 Testing user registration...")
    
    # Create test user data
    test_user = {
        "username": f"test_user_{datetime.now().timestamp()}",
        "email": f"test_{datetime.now().timestamp()}@test.com",
        "password": "test_password123"
    }
    
    try:
        # First verify the endpoint is accessible
        logger.info(f"Attempting to register user: {test_user['username']}")
        response = requests.post(
            f"{BASE_URL}/users/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        # Log the complete response for debugging
        logger.info(f"Response Status Code: {response.status_code}")
        logger.info(f"Response Headers: {dict(response.headers)}")
        try:
            logger.info(f"Response Body: {response.json()}")
        except:
            logger.info(f"Response Text: {response.text}")

        if response.status_code == 201:
            user_id = response.json().get("id")
            if user_id:
                logger.info(f"✅ User registration successful. User ID: {user_id}")
                return user_id
            else:
                logger.error("❌ User ID not found in successful response")
                return None
        elif response.status_code == 422:
            logger.error("❌ Validation error in request data:")
            logger.error(response.json())
            return None
        elif response.status_code == 500:
            logger.error("❌ Server error during registration")
            logger.error(f"Error details: {response.text}")
            return None
        else:
            logger.error(f"❌ Unexpected status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError as e:
        logger.error("❌ Connection error during registration")
        logger.error(f"Error details: {str(e)}")
        logger.info("Please ensure the server is running and accessible")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error during registration: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        return None

def test_user_login(email: str, password: str):
    """Test user login endpoint"""
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/login", json=login_data)
        assert response.status_code == 200
        logger.info("✅ User login test passed")
        return response.json()["user_id"]
    except Exception as e:
        logger.error(f"❌ User login test failed: {str(e)}")
        return None

def test_baseline_schedule(user_id: int):
    """Test setting and getting baseline schedule"""
    baseline_schedule = {
        "user_id": user_id,
        "tasks": [
            {
                "task_name": "Morning Exercise",
                "scheduled_time": "07:00:00",
                "goal_time": "07:30:00"
            },
            {
                "task_name": "Reading",
                "scheduled_time": "20:00:00",
                "goal_time": "20:30:00"
            }
        ]
    }
    
    try:
        # Set baseline schedule
        response = requests.post(f"{BASE_URL}/baseline_schedule/set", json=baseline_schedule)
        assert response.status_code == 200
        logger.info("✅ Setting baseline schedule test passed")

        # Get baseline schedule
        response = requests.get(
            f"{BASE_URL}/baseline_schedule/{user_id}",
            headers={"User-Timezone": "UTC"}
        )
        assert response.status_code == 200
        logger.info("✅ Getting baseline schedule test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Baseline schedule test failed: {str(e)}")
        return False

def test_daily_schedule_generation(user_id: int):
    """Test daily schedule generation"""
    try:
        response = requests.post(f"{BASE_URL}/daily_schedule/generate/{user_id}")
        assert response.status_code == 200
        logger.info("✅ Daily schedule generation test passed")

        # Get generated schedule
        response = requests.get(
            f"{BASE_URL}/daily_schedule/{user_id}",
            headers={"User-Timezone": "UTC"}
        )
        assert response.status_code == 200
        logger.info("✅ Getting daily schedule test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Daily schedule generation test failed: {str(e)}")
        return False

def test_task_logging(user_id: int):
    """Test task logging functionality"""
    task_log = {
        "tasks": [
            {
                "user_id": user_id,
                "task_name": "Morning Exercise",
                "completed": True,
                "actual_completed_time": "07:15:00",
                "log_date": datetime.now().strftime("%Y-%m-%d")
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tasks/log", json=task_log)
        assert response.status_code == 200
        logger.info("✅ Task logging test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Task logging test failed: {str(e)}")
        return False

def test_ai_habit_adjustments(user_id: int):
    """Test AI habit adjustments"""
    try:
        # Generate AI adjustments
        response = requests.get(f"{BASE_URL}/ai/habit_adjustments/{user_id}")
        assert response.status_code == 200
        logger.info("✅ AI habit adjustments generation test passed")

        # Test responding to an adjustment
        adjustment_response = {
            "habit": "Morning Exercise",
            "status": "accepted"
        }
        response = requests.post(
            f"{BASE_URL}/ai/habit_adjustments/respond/{user_id}",
            json=adjustment_response
        )
        assert response.status_code == 200
        logger.info("✅ AI habit adjustment response test passed")
        return True
    except Exception as e:
        logger.error(f"❌ AI habit adjustments test failed: {str(e)}")
        return False

def test_database_connection():
    """Test database and Redis connections"""
    logger.info("🔄 Testing database connections...")
    
    # Test PostgreSQL connection
    try:
        # Update these values according to your database configuration
        DATABASE_URL = "postgresql://user:password@localhost:5432/gradually_ai"
        engine = create_engine(DATABASE_URL)
        engine.connect()
        logger.info("✅ PostgreSQL connection successful")
    except Exception as e:
        logger.error("❌ PostgreSQL connection failed")
        logger.error(f"Error details: {str(e)}")
        return False

    # Test Redis connection
    try:
        redis_client = redis.Redis(host="localhost", port=6379, db=0)
        redis_client.ping()
        logger.info("✅ Redis connection successful")
    except Exception as e:
        logger.error("❌ Redis connection failed")
        logger.error(f"Error details: {str(e)}")
        return False

    return True

def run_all_tests():
    """Run all API tests in sequence"""
    logger.info("🔄 Starting API tests...")
    
    # Test database connections first
    if not test_database_connection():
        logger.error("❌ Stopping tests due to database connection failure")
        return
    
    # Test health check
    if not test_health_check():
        logger.error("❌ Stopping tests due to failed health check")
        return
    
    # Test user registration and login
    test_email = f"test_{datetime.now().timestamp()}@test.com"
    test_password = "test_password123"
    
    user_id = test_user_registration()
    if not user_id:
        logger.error("❌ Stopping tests due to failed user registration")
        return
    
    if not test_user_login(test_email, test_password):
        logger.error("❌ Stopping tests due to failed login")
        return
    
    # Test schedule-related endpoints
    if not test_baseline_schedule(user_id):
        logger.error("❌ Stopping tests due to failed baseline schedule test")
        return
    
    if not test_daily_schedule_generation(user_id):
        logger.error("❌ Stopping tests due to failed daily schedule generation")
        return
    
    if not test_task_logging(user_id):
        logger.error("❌ Stopping tests due to failed task logging")
        return
    
    if not test_ai_habit_adjustments(user_id):
        logger.error("❌ Stopping tests due to failed AI habit adjustments")
        return
    
    logger.info("✅ All API tests completed successfully!")

if __name__ == "__main__":
    run_all_tests() 