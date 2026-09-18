from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from dotenv import load_dotenv
import os
from sqlalchemy import inspect

# Load environment variables
load_dotenv()

# Create Base class for models
Base = declarative_base()

# Retrieve DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is missing from .env. Make sure the .env file exists and contains DATABASE_URL.")

# Set up database engine with more detailed logging
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log all SQL
    echo_pool=True,  # Log connection pool events
    pool_pre_ping=True,  # Verify connection before using
    future=True  # Use SQLAlchemy 2.0 style
)

# Create a scoped session factory
session_factory = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)
SessionLocal = scoped_session(session_factory)

# Add query property to Base
Base.query = SessionLocal.query_property()

# Test connection
def test_connection():
    db = SessionLocal()
    try:
        # Basic connection test
        result = db.execute(text("SELECT 1"))
        db.commit()
        print("✅ Database connection successful!")

        # Check if we can access the tables
        result = db.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"))
        tables = [row[0] for row in result]
        print(f"📋 Accessible tables: {tables}")

        # Try to select from users table
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        print(f"👥 Users table exists with {count} rows")
        
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Database error: {str(e)}")
        return False
    finally:
        db.close()  # Close the session instead of removing it

# Context manager for database sessions
def get_db_context():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()  # Close the session instead of removing it

async def init_db():
    """Initialize database tables if they don't exist."""
    try:
        # Import all models to ensure they're registered with SQLAlchemy
        print("🔄 Importing models...")
        from .models.user import User
        from .models.baseline_schedule import BaselineSchedule
        from .models.daily_schedule import DailySchedule
        from .models.task import Task
        from .models.habit import HabitAdjustment, ScheduleAdjustment
        
        print("🔄 Checking database tables...")
        
        # Get list of tables before creation
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        print(f"📋 Existing tables before creation: {existing_tables}")
        
        # Create all tables
        print("🔨 Creating missing tables...")
        Base.metadata.create_all(bind=engine)
        
        # Get list of tables after creation
        inspector = inspect(engine)
        tables_after = inspector.get_table_names()
        print(f"📋 Tables after creation: {tables_after}")
        
        # List newly created tables
        new_tables = set(tables_after) - set(existing_tables)
        if new_tables:
            print(f"✅ Newly created tables: {new_tables}")
        else:
            print("ℹ️ No new tables needed to be created")
        
        # Verify users table exists
        if "users" in tables_after:
            print("✅ Users table exists")
            # Try a simple query
            session = SessionLocal()
            try:
                count = session.query(User).count()
                print(f"👥 Current user count: {count}")
            finally:
                session.close()
        else:
            print("❌ Users table is missing!")
        
        print("✅ Database initialization complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error during database initialization: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

# Export commonly used items
__all__ = ['Base', 'SessionLocal', 'get_db_context', 'init_db']

# Only test connection if this file is run directly
if __name__ == "__main__":
    test_connection()
    init_db()  # Run initialization if this script is executed directly 