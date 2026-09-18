from datetime import datetime, time
import pytz
from typing import Optional

class TimeUtils:
    @staticmethod
    def validate_timezone(timezone_str: str) -> bool:
        """Validate if a timezone string is valid."""
        try:
            pytz.timezone(timezone_str)
            return True
        except pytz.exceptions.UnknownTimeZoneError:
            return False

    @staticmethod
    def parse_time_string(time_str: Optional[str]) -> Optional[time]:
        """Parse a time string into a time object."""
        if not time_str:
            return None
        try:
            return datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            raise ValueError(f"Invalid time format: {time_str}. Expected format: HH:MM")

    @staticmethod
    def get_current_time(timezone_str: str) -> datetime:
        """Get current time in specified timezone."""
        try:
            tz = pytz.timezone(timezone_str)
            return datetime.now(tz)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f"Invalid timezone: {timezone_str}")

    @staticmethod
    def convert_timezone(dt: datetime, target_tz_str: str) -> datetime:
        """Convert a datetime to target timezone."""
        if not dt.tzinfo:
            dt = pytz.UTC.localize(dt)
        target_tz = pytz.timezone(target_tz_str)
        return dt.astimezone(target_tz) 