from database import engine, Base  # Import engine and Base from database.py

def init_db():
    """Initialize database tables if they don't exist."""
    print("🔄 Checking database tables...")
    Base.metadata.create_all(bind=engine)  # Creates tables if they don’t exist
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    init_db()  # Run initialization if this script is executed directly
