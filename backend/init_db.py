import asyncio
from database import init_db, test_connection

async def main():
    print("🔄 Testing database connection...")
    if test_connection():
        print("✅ Database connection successful!")
        print("\n🔄 Initializing database tables...")
        if await init_db():
            print("✅ Database initialization successful!")
        else:
            print("❌ Database initialization failed!")
    else:
        print("❌ Database connection failed!")

if __name__ == "__main__":
    asyncio.run(main()) 