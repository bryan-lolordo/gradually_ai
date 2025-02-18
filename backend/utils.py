from datetime import datetime
import pytz

# Define Central Time Zone
CST = pytz.timezone("America/Chicago")

def get_current_time_cst():
    """Returns the current timestamp in CST."""
    return datetime.now(CST)

def convert_to_cst(dt: datetime):
    """Converts a given datetime to CST."""
    return dt.astimezone(CST) if dt else None
