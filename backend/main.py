from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth, baseline_schedule, daily_schedule, tasks, habits
from database import init_db
import logging
from config.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Gradually API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    await init_db()
    logger.info("✅ Database initialized")
    logger.info("✅ Redis cache initialized")

# Include routers
app.include_router(auth.router, prefix="/users", tags=["Authentication"])
app.include_router(baseline_schedule.router, prefix="/baseline-schedule", tags=["Baseline Schedule"])
app.include_router(daily_schedule.router, prefix="/daily-schedule", tags=["Daily Schedule"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(habits.router, prefix="/habits", tags=["Habits"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"} 