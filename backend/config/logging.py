import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging():
    """Configure logging for the application."""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = f"logs/app_{timestamp}.log"

    # Configure logging format
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # File handler with rotation
            logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10485760,  # 10MB
                backupCount=5,
                encoding="utf-8"
            ),
            # Console handler
            logging.StreamHandler()
        ]
    )

    # Set more verbose logging for certain modules
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("uvicorn").setLevel(logging.INFO)

    # Create logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Logging setup completed") 