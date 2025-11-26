# Time Formatting API

A FastAPI application that converts 24-hour times (HH:MM) into 12-hour format with AM/PM notation.

## Features

- Formats time in 12-hour format with AM/PM ("standard" time)
- Accepts 24-hour input times in `HH:MM` format (e.g., `00:05`, `14:30`, `23:59`)
- Simple RESTful HTTP API

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the application (choose one):
```bash
# Python entry point
python main.py

# Or using the run script (if present)
python run.py

# Or start via uvicorn explicitly
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

The API will be available at `http://localhost:8001`.

## Connecting to the Service

- Base URL: `http://localhost:8001`
- All requests and responses use JSON.
- For POST requests, include header `Content-Type: application/json`.

## Endpoints (Communication Contract)

### Format Time (standard 12-hour)

- Path: `/format/standard`
- Method: `POST`
- Content-Type: `application/json`

Required request body fields:
- `time` (string, required): A time in 24-hour `HH:MM` format.

Optional fields: none

Input requirements and validation:
- `HH` must be `00`–`23`; `MM` must be `00`–`59`.
- Invalid or misformatted times return `400 Bad Request` with an error message.

Successful response (`200 OK`):
```json
{
  "original_time": "14:30",
  "formatted_time": "2:30 PM",
  "format": "standard"
}
```

## How to Request (before examples)

1) Ensure the service is running on `http://localhost:8001`.
2) Send an HTTP `POST` to `/format/standard` with JSON body containing a single `time` field in `HH:MM` format.
3) Set header `Content-Type: application/json`.
4) Expect a JSON response with the original and formatted time, or a `400` error for invalid input.

## Example Requests

Using Python (`requests`):
```python
import requests

url = "http://localhost:8001/format/standard"
payload = {"time": "14:30"}
resp = requests.post(url, json=payload, timeout=5)
if resp.status_code == 200:
    data = resp.json()
    print("Original:", data.get("original_time"))
    print("Formatted:", data.get("formatted_time"))
else:
    print("Error:", resp.status_code, resp.text)
```

## Receiving and Handling Responses

- Success: status `200` with JSON body containing `original_time`, `formatted_time`, and `format`.
- Client error: status `400` for invalid `time` format. The response includes an error message explaining the issue.