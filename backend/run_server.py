import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🚀 Starting FastAPI server...")
    
    # Configure server
    config = {
        "app": "api:app",  # Path to your FastAPI app
        "host": "0.0.0.0", # Allows external access
        "port": 8000,      # Port number
        "reload": True,    # Auto-reload on code changes
        "workers": 1       # Number of worker processes
    }
    
    try:
        logger.info(f"Server will be available at http://localhost:{config['port']}")
        uvicorn.run(**config)
    except Exception as e:
        logger.error(f"❌ Failed to start server: {str(e)}") 