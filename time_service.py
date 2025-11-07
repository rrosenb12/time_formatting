from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional
import json
import os

app = FastAPI(title="Time Formatting Microservice")

# Data storage for user timezone preferences
TIMEZONES_FILE = "timezone_preferences.json"

# Pydantic models
class TimeConversionRequest(BaseModel):
    time_str: str
    from_timezone: str
    to_timezone: str
    date_str: Optional[str] = None  # Optional date for context

class TimeConversionResponse(BaseModel):
    original_time: str
    original_timezone: str
    converted_time: str
    converted_timezone: str
    is_dst: bool

class UserTimezonePreference(BaseModel):
    user_id: str
    preferred_timezone: str

class TimezoneListResponse(BaseModel):
    timezones: List[str]
    total_count: int

# Helper functions for JSON storage
def load_timezone_preferences() -> Dict[str, str]:
    """Load timezone preferences from JSON file"""
    if os.path.exists(TIMEZONES_FILE):
        with open(TIMEZONES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_timezone_preferences(preferences: Dict[str, str]):
    """Save timezone preferences to JSON file"""
    with open(TIMEZONES_FILE, 'w') as f:
        json.dump(preferences, f, indent=2)

def get_common_timezones() -> List[str]:
    """Return a list of common timezones"""
    return [
        'UTC',
        'US/Eastern',
        'US/Central', 
        'US/Mountain',
        'US/Pacific',
        'Europe/London',
        'Europe/Paris',
        'Europe/Berlin',
        'Asia/Tokyo',
        'Asia/Shanghai',
        'Australia/Sydney',
        'Pacific/Auckland'
    ]

# API endpoints
@app.post("/time/convert", response_model=TimeConversionResponse)
async def convert_time(conversion_request: TimeConversionRequest):
    """
    Convert time between timezones
    
    BENEFITS: Accurate timezone conversion for global collaboration
    COSTS: Limited to common timezones; requires valid time format
    """
    try:
        # Parse the time (with optional date)
        if conversion_request.date_str:
            datetime_str = f"{conversion_request.date_str} {conversion_request.time_str}"
            time_format = "%Y-%m-%d %H:%M:%S"
        else:
            datetime_str = conversion_request.time_str
            time_format = "%H:%M:%S"
        
        # Create naive datetime and localize
        naive_dt = datetime.strptime(datetime_str, time_format)
        
        # Localize to source timezone
        from_tz = pytz.timezone(conversion_request.from_timezone)
        localized_dt = from_tz.localize(naive_dt) if conversion_request.date_str else from_tz.localize(
            datetime.combine(datetime.today(), naive_dt.time())
        )
        
        # Convert to target timezone
        to_tz = pytz.timezone(conversion_request.to_timezone)
        converted_dt = localized_dt.astimezone(to_tz)
        
        # Check if DST is active
        is_dst = bool(converted_dt.dst())
        
        return TimeConversionResponse(
            original_time=conversion_request.time_str,
            original_timezone=conversion_request.from_timezone,
            converted_time=converted_dt.strftime("%H:%M:%S"),
            converted_timezone=conversion_request.to_timezone,
            is_dst=is_dst
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid time format: {e}")
    except pytz.exceptions.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail="Unknown timezone")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {e}")

@app.get("/time/timezones", response_model=TimezoneListResponse)
async def list_timezones():
    """
    Get list of available timezones
    
    BENEFITS: Browse supported timezones for selection
    COSTS: Limited predefined set; no custom timezones
    """
    timezones = get_common_timezones()
    return TimezoneListResponse(
        timezones=timezones,
        total_count=len(timezones)
    )

@app.post("/time/preferences")
async def set_timezone_preference(preference: UserTimezonePreference):
    """
    Set user's preferred timezone
    
    BENEFITS: Save preferred timezone for future conversions
    COSTS: Requires user authentication; preferences stored locally
    """
    preferences = load_timezone_preferences()
    preferences[preference.user_id] = preference.preferred_timezone
    save_timezone_preferences(preferences)
    
    return {"message": "Timezone preference saved", "user_id": preference.user_id}

@app.get("/time/preferences/{user_id}")
async def get_timezone_preference(user_id: str):
    """
    Get user's preferred timezone
    """
    preferences = load_timezone_preferences()
    preferred_tz = preferences.get(user_id, "UTC")
    
    return {
        "user_id": user_id,
        "preferred_timezone": preferred_tz,
        "exists": user_id in preferences
    }

@app.get("/time/current")
async def get_current_time(timezone: str = "UTC"):
    """
    Get current time in specified timezone
    """
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        is_dst = bool(current_time.dst())
        
        return {
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "timezone": timezone,
            "is_dst": is_dst,
            "timezone_offset": current_time.strftime("%z")
        }
    except pytz.exceptions.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail="Unknown timezone")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "time_formatting"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)