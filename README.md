# Time Formatting API

A FastAPI application that allows users to format time.

## Features

- Format time in 12-hour format with AM/PM notation (standard time)
- Accepts time input in HH:MM format
- RESTful API

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

Or using the run script:
```bash
python run.py
```

Or using uvicorn directly (port must be specified):
```bash
uvicorn main:app --reload --port 8001
```

The API will be available at `http://localhost:8001`

## Usage

### Format Time Endpoint

**POST** `/format/standard`

Request body:
```json
{
  "time": "14:30"
}
```

Response:
```json
{
  "original_time": "14:30",
  "formatted_time": "2:30 PM",
  "format": "standard"
}
```

### Example Requests

**Standard time (12-hour format):**
```bash
curl -X POST "http://localhost:8001/format/standard" \
  -H "Content-Type: application/json" \
  -d '{"time": "14:30"}'
```

## UML Diagram

[Time Formatting Sequence Diagram.pdf](https://github.com/user-attachments/files/23565124/Time.Formatting.Sequence.Diagram.pdf)

