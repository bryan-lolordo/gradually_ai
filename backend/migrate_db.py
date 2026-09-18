from database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    try:
        # Add updated_at column if it doesn't exist
        with engine.connect() as connection:
            # Check if column exists
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'updated_at';
            """))
            
            if not result.fetchone():
                logger.info("Adding updated_at column to users table...")
                connection.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE 
                    DEFAULT CURRENT_TIMESTAMP;
                """))
                connection.commit()
                logger.info("✅ Successfully added updated_at column")
            else:
                logger.info("✅ updated_at column already exists")
            
            # List all columns in users table
            result = connection.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users';
            """))
            columns = result.fetchall()
            logger.info("Current users table columns:")
            for col in columns:
                logger.info(f"  - {col[0]} ({col[1]})")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    migrate() 