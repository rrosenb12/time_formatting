#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict
import pytz

app = FastAPI(title="Time Formatting / Conversion Microservice", version="1.1.0")

# --------------------------------------------------------------------
# Supported timezones (user-facing abbreviations) and mapping
# --------------------------------------------------------------------
SUPPORTED_ABBR: List[str] = ["EST", "CST", "PST", "UTC"]

ABBR_TO_IANA: Dict[str, str] = {
    "EST": "US/Eastern",
    "CST": "US/Central",
    "PST": "US/Pacific",
    "UTC": "UTC",
}

# Allow a small set of legacy IANA inputs, but normalize to the abbreviations above.
IANA_TO_ABBR: Dict[str, str] = {
    "US/Eastern": "EST",
    "US/Central": "CST",
    "US/Pacific": "PST",
    "UTC": "UTC",
}

def resolve_abbr(tz: str) -> str:
    """
    Accept only our four abbreviations; allow legacy IANA names and normalize them.
    Raise HTTP 400 for anything else.
    """
    if tz in SUPPORTED_ABBR:
        return tz
    if tz in IANA_TO_ABBR:
        return IANA_TO_ABBR[tz]
    raise HTTPException(status_code=400, detail=f"Unknown or unsupported timezone: {tz}. "
                                                f"Allowed: {', '.join(SUPPORTED_ABBR)}")

def abbr_to_tzinfo(abbr: str):
    iana = ABBR_TO_IANA[abbr]
    try:
        return pytz.timezone(iana)
    except pytz.UnknownTimeZoneError:
        # Should never happen with our fixed set
        raise HTTPException(status_code=500, detail=f"Server timezone config error: {iana}")

# --------------------------------------------------------------------
# Models
# --------------------------------------------------------------------
class TimeConversionRequest(BaseModel):
    time_str: str                 # "HH:MM:SS"
    from_timezone: str            # one of EST/CST/PST/UTC (or legacy mapping)
    to_timezone: str              # one of EST/CST/PST/UTC (or legacy mapping)
    date_str: Optional[str] = None  # "YYYY-MM-DD" for DST correctness (recommended)

class TimeConversionResponse(BaseModel):
    original_time: str
    original_timezone: str
    converted_time: str
    converted_timezone: str
    is_dst: bool

class TimezoneListResponse(BaseModel):
    timezones: List[str]
    total_count: int

# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------
def parse_time_hms(hms: str) -> datetime:
    """
    Parse "HH:MM:SS" into a datetime on an arbitrary date (we'll replace date later).
    Raise HTTP 400 for invalid format.
    """
    try:
        return datetime.strptime(hms.strip(), "%H:%M:%S")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid time_str format: {e}. Expected 'HH:MM:SS'.")

def parse_date(date_s: Optional[str]) -> Optional[datetime]:
    """
    Parse "YYYY-MM-DD" into a date (no time component). If None, return None.
    """
    if not date_s:
        return None
    try:
        return datetime.strptime(date_s.strip(), "%Y-%m-%d")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date_str format: {e}. Expected 'YYYY-MM-DD'.")

# --------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------
@app.post("/time/convert", response_model=TimeConversionResponse)
async def convert_time(conversion_request: TimeConversionRequest):
    """
    Convert time between EST/CST/PST/UTC in 24-hour format.
    - time_str: "HH:MM:SS"
    - from_timezone / to_timezone: EST | CST | PST | UTC (IANA accepted but normalized)
    - date_str: "YYYY-MM-DD" (recommended, to ensure correct DST at that date)
    """
    # Normalize tz inputs to our abbreviations; map to tzinfo
    from_abbr = resolve_abbr(conversion_request.from_timezone)
    to_abbr   = resolve_abbr(conversion_request.to_timezone)
    from_tz   = abbr_to_tzinfo(from_abbr)
    to_tz     = abbr_to_tzinfo(to_abbr)

    # Parse time and (optional) date
    hms_dt = parse_time_hms(conversion_request.time_str)
    date_dt = parse_date(conversion_request.date_str)

    # Build the source naive datetime using provided date (or today's date if missing)
    if date_dt:
        naive_src = datetime(year=date_dt.year, month=date_dt.month, day=date_dt.day,
                             hour=hms_dt.hour, minute=hms_dt.minute, second=hms_dt.second)
    else:
        today = datetime.now(pytz.utc).astimezone(from_tz)  # today in source tz
        naive_src = datetime(year=today.year, month=today.month, day=today.day,
                             hour=hms_dt.hour, minute=hms_dt.minute, second=hms_dt.second)

    # Localize to source tz and convert
    try:
        localized_src = from_tz.localize(naive_src, is_dst=None)  # let pytz decide; may raise for gaps/folds
    except Exception as e:
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
    """
    List ONLY the allowed display timezones.
    """
    return TimezoneListResponse(
        timezones=SUPPORTED_ABBR,
        total_count=len(SUPPORTED_ABBR)
    )

@app.get("/time/current")
async def get_current_time(timezone: str = Query("UTC", description="EST | CST | PST | UTC")):
    """
    Get the current time in one of the allowed timezones, in 24-hour format.
    """
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

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "time_formatting"}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)