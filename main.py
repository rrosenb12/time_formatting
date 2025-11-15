from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import time
import re
from datetime import datetime
from typing import List, Optional, Dict
import pytz
from pytz.exceptions import AmbiguousTimeError, NonExistentTimeError
from fastapi import Query

app = FastAPI(title="Time Formatting API", version="1.0.0", docs_url=None, redoc_url=None)


class TimeFormatRequest(BaseModel):
    time: str = Field(..., description="Time input in HH:MM format (24-hour)")


class TimeFormatResponse(BaseModel):
    original_time: str
    formatted_time: str
    format: str = "standard"


# --- Timezone conversion models and helpers ---
class TimeConversionRequest(BaseModel):
    time_str: str                 # "HH:MM:SS"
    from_timezone: str            # one of EST/CST/PST/UTC (or legacy mapping)
    to_timezone: str              # one of EST/CST/PST/UTC (or legacy mapping)
    date_str: Optional[str] = None  # "YYYY-MM-DD" for DST correctness (optional)


class TimeConversionResponse(BaseModel):
    original_time: str
    original_timezone: str
    converted_time: str
    converted_timezone: str
    is_dst: bool


class TimezoneListResponse(BaseModel):
    timezones: List[str]
    total_count: int


# Supported abbreviations and mappings
SUPPORTED_ABBR: List[str] = ["EST", "CST", "PST", "UTC"]

ABBR_TO_IANA: Dict[str, str] = {
    "EST": "US/Eastern",
    "CST": "US/Central",
    "PST": "US/Pacific",
    "UTC": "UTC",
}

IANA_TO_ABBR: Dict[str, str] = {v: k for k, v in ABBR_TO_IANA.items()}


def resolve_abbr(tz: str) -> str:
    if tz in SUPPORTED_ABBR:
        return tz
    if tz in IANA_TO_ABBR:
        return IANA_TO_ABBR[tz]
    raise HTTPException(status_code=400, detail=f"Unknown or unsupported timezone: {tz}. Allowed: {', '.join(SUPPORTED_ABBR)}")


def abbr_to_tzinfo(abbr: str):
    iana = ABBR_TO_IANA[abbr]
    try:
        return pytz.timezone(iana)
    except pytz.UnknownTimeZoneError:
        raise HTTPException(status_code=500, detail=f"Server timezone config error: {iana}")


def parse_time_hms(hms: str) -> datetime:
    try:
        return datetime.strptime(hms.strip(), "%H:%M:%S")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid time_str format: {e}. Expected 'HH:MM:SS'.")


def parse_date(date_s: Optional[str]) -> Optional[datetime]:
    if not date_s:
        return None
    try:
        return datetime.strptime(date_s.strip(), "%Y-%m-%d")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date_str format: {e}. Expected 'YYYY-MM-DD'.")


def parse_time(time_str: str) -> time:
    """
    Parse time string in HH:MM format and return a time object.
    """
    # Remove whitespace
    time_str = time_str.strip()
    
    # Parse HH:MM format
    pattern = r'^(\d{1,2}):(\d{2})$'
    match = re.match(pattern, time_str)
    
    if not match:
        raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM format")
    
    hour = int(match.group(1))
    minute = int(match.group(2))
    
    # Validate ranges
    if hour < 0 or hour > 23:
        raise ValueError(f"Hour must be between 0 and 23, got {hour}")
    if minute < 0 or minute > 59:
        raise ValueError(f"Minute must be between 0 and 59, got {minute}")
    
    return time(hour, minute)


def format_time_standard(time_obj: time) -> str:
    """
    Format time in 12-hour format with AM/PM notation.
    """
    hour = time_obj.hour
    minute = time_obj.minute
    
    # Convert to 12-hour format
    if hour == 0:
        hour_12 = 12
        period = "AM"
    elif hour < 12:
        hour_12 = hour
        period = "AM"
    elif hour == 12:
        hour_12 = 12
        period = "PM"
    else:
        hour_12 = hour - 12
        period = "PM"
    
    return f"{hour_12}:{minute:02d} {period}"


@app.get("/")
async def root():
    return {
        "message": "Time Formatting API",
        "endpoints": {
            "/format/standard": "POST - Format time in standard (12-hour) format with AM/PM"
        }
    }


@app.post("/format/standard", response_model=TimeFormatResponse)
async def format_time(request: TimeFormatRequest):
    """
    Format a time string in standard (12-hour) format with AM/PM notation.
    
    - **time**: Time in HH:MM format (24-hour input)
    
    Returns the formatted time string in 12-hour format with AM/PM.
    """
    try:
        # Parse the input time
        time_obj = parse_time(request.time)
        
        # Format in standard (12-hour) format
        formatted = format_time_standard(time_obj)
        
        return TimeFormatResponse(
            original_time=request.time,
            formatted_time=formatted,
            format="standard"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# --- Timezone conversion endpoints ---
@app.post("/time/convert", response_model=TimeConversionResponse)
async def convert_time(conversion_request: TimeConversionRequest):
    # Normalize tz inputs
    from_abbr = resolve_abbr(conversion_request.from_timezone)
    to_abbr = resolve_abbr(conversion_request.to_timezone)
    from_tz = abbr_to_tzinfo(from_abbr)
    to_tz = abbr_to_tzinfo(to_abbr)

    hms_dt = parse_time_hms(conversion_request.time_str)
    date_dt = parse_date(conversion_request.date_str)

    if date_dt:
        naive_src = datetime(year=date_dt.year, month=date_dt.month, day=date_dt.day,
                             hour=hms_dt.hour, minute=hms_dt.minute, second=hms_dt.second)
    else:
        today = datetime.now(pytz.utc).astimezone(from_tz)
        naive_src = datetime(year=today.year, month=today.month, day=today.day,
                             hour=hms_dt.hour, minute=hms_dt.minute, second=hms_dt.second)

    try:
        localized_src = from_tz.localize(naive_src, is_dst=None)
    except (AmbiguousTimeError, NonExistentTimeError) as e:
        raise HTTPException(status_code=400, detail=f"Failed to localize source time: {e}")

    converted = localized_src.astimezone(to_tz)
    is_dst = bool(converted.dst())

    return TimeConversionResponse(
        original_time=conversion_request.time_str,
        original_timezone=from_abbr,
        converted_time=converted.strftime("%H:%M:%S"),
        converted_timezone=to_abbr,
        is_dst=is_dst
    )


@app.get("/time/timezones", response_model=TimezoneListResponse)
async def list_timezones():
    return TimezoneListResponse(timezones=SUPPORTED_ABBR, total_count=len(SUPPORTED_ABBR))


@app.get("/time/current")
async def get_current_time(timezone: str = Query("UTC", description="EST | CST | PST | UTC")):
    abbr = resolve_abbr(timezone)
    tz = abbr_to_tzinfo(abbr)
    current_time = datetime.now(tz)
    is_dst = bool(current_time.dst())

    return {
        "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": abbr,
        "is_dst": is_dst,
        "timezone_offset": current_time.strftime("%z")
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

