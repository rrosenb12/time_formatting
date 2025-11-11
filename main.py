from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import time
import re

app = FastAPI(title="Time Formatting API", version="1.0.0", docs_url=None, redoc_url=None)


class TimeFormatRequest(BaseModel):
    time: str = Field(..., description="Time input in HH:MM format (24-hour)")


class TimeFormatResponse(BaseModel):
    original_time: str
    formatted_time: str
    format: str = "standard"


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

