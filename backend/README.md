# Backend Documentation

## Timezone Handling

The application uses the `TimeUtils` class in `utils.py` for all timezone-related operations. This ensures consistent timezone handling across the application.

### Key Features

- Timezone validation
- Time string parsing
- Datetime formatting
- Time range validation
- User timezone conversion

### Usage Examples

```python
from utils import TimeUtils, get_user_local_time, convert_to_user_timezone

# Get all available timezones
timezones = TimeUtils.get_available_timezones()

# Validate a timezone
is_valid = TimeUtils.validate_timezone("Europe/London")

# Get current time in a specific timezone
london_time = TimeUtils.get_current_time("Europe/London")

# Convert between timezones
utc_time = datetime.now(pytz.UTC)
ny_time = TimeUtils.convert_timezone(utc_time, "America/New_York")

# Parse time strings
task_time = TimeUtils.parse_time_string("14:30")

# Format datetime objects
formatted = TimeUtils.format_datetime(some_datetime, "%Y-%m-%d %H:%M")

# Validate time ranges
is_valid = TimeUtils.is_valid_time_range(start_time, end_time)

# User timezone convenience functions
user_time = get_user_local_time(user.timezone)
local_time = convert_to_user_timezone(utc_time, user.timezone)
```

### Best Practices

1. **Always Store in UTC**
   - Store all timestamps in UTC in the database
   - Convert to user's timezone only for display

2. **Validate Timezones**
   - Always validate user-provided timezone strings
   - Use `TimeUtils.validate_timezone()` for validation

3. **Time String Parsing**
   - Use `TimeUtils.parse_time_string()` for parsing time strings
   - Handles invalid formats and provides clear error messages

4. **Timezone Conversion**
   - Use `convert_to_user_timezone()` for user-specific conversions
   - Always ensure datetime objects are timezone-aware

5. **Format Consistency**
   - Use `TimeUtils.format_datetime()` for consistent datetime formatting
   - Default format includes timezone information

### Deprecated Functions

The following functions are maintained for backward compatibility but should not be used in new code:

- `get_current_time_cst()`
- `convert_to_cst()`

Instead, use the timezone-agnostic functions with "America/Chicago" as the timezone parameter when CST is needed.

## Models

The application uses timezone-aware models:

```python
class User(Base):
    timezone = Column(String, default="UTC")

class BaselineSchedule(Base):
    scheduled_time = Column(Time, nullable=False)  # Stored in UTC
    user_timezone = Column(String, nullable=False)
```

## API Endpoints

Timezone handling in API endpoints:

1. **Request Headers**
   - Accept user timezone in 'User-Timezone' header
   - Validate timezone before use

2. **Response Data**
   - Convert times to user's timezone before sending
   - Include timezone information in responses

## Testing

When writing tests:

1. Use explicit timezones in test data
2. Test timezone conversion edge cases
3. Verify timezone-aware datetime comparisons
4. Test invalid timezone handling 