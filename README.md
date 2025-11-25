# Time Formatting API

A FastAPI microservice that formats times and provides a simple HTTP API. This README now includes the communication contract required by the assignment: how to programmatically request data, how the service responds, an example test program, and an example UML sequence diagram placeholder.

## Getting Started

### Prerequisites
- Python 3.7 or higher
- The microservice must be running on your local machine or network
- Python library: `requests` (install with `pip install requests`)

### Starting the Service
The service runs on **port 8001** by default. Start it using:
```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

Or using the provided run script:
```bash
python run.py
```

### Connecting to the Service
All requests are made to `http://localhost:8001` (or the appropriate host/port where the service is running).

The service uses RESTful HTTP methods:
- **POST** for formatting time requests
- **GET** for retrieving available timezones

All POST requests must include `Content-Type: application/json` header and send data as JSON in the request body.

## Service Endpoints (Contract)

- **Format time (standard / 12-hour)**: `POST /format/standard`
  - Request (Content-Type: application/json):
    ```json
    { "time": "14:30" }
    ```
  - Successful response (`200 OK`):
    ```json
    {
      "original_time": "14:30",
      "formatted_time": "2:30 PM",
      "format": "standard"
    }
    ```
  - Error responses: `400 Bad Request` for invalid time formats, with JSON describing the error.

- **List timezones (optional helper)**: `GET /time/timezones`
  - Response: JSON list of supported timezone strings (if implemented).

IMPORTANT: This is the communication contract. Do not change request/response shapes without coordinating with your teammates.

## How to programmatically REQUEST data (detailed guide)

### 1. Format Time to Standard 12-Hour Format (`POST /format/standard`)

**Purpose**: Convert 24-hour time format (e.g., "14:30") to 12-hour format with AM/PM (e.g., "2:30 PM").

**Connection Details**:
- URL: `http://localhost:8001/format/standard`
- Method: POST
- Content-Type: application/json

**Required Parameters**:
- `time` (string): Time in 24-hour format (HH:MM). Examples: "14:30", "09:15", "23:45"

**Optional Parameters**: None

**Time Format Requirements**:
- Must be in HH:MM format
- Hours: 00-23
- Minutes: 00-59
- Invalid formats will return a 400 Bad Request error

**Example Requests Using Different Tools**:

- Curl (PowerShell-friendly):

```powershell
curl -X POST "http://localhost:8001/format/standard" `
  -H "Content-Type: application/json" `
  -d '{"time": "14:30"}'
```

- Python (`requests`) — sending a request:

```python
import requests

url = "http://localhost:8001/format/standard"
resp = requests.post(url, json={"time": "14:30"}, timeout=5)
resp.raise_for_status()
data = resp.json()
print("Received:", data)
```

### 2. List Available Timezones (`GET /time/timezones`)

**Purpose**: Retrieve a list of all supported timezone strings (if implemented).

**Connection Details**:
- URL: `http://localhost:8001/time/timezones`
- Method: GET
- Content-Type: Not required for GET requests

**Required Parameters**: None

**Optional Parameters**: None

**Example Request**:

```python
import requests

url = "http://localhost:8001/time/timezones"
resp = requests.get(url, timeout=5)
resp.raise_for_status()
timezones = resp.json()
print("Available timezones:", timezones)
```

## Receiving Data (examples)

These examples show what the client receives and how to handle the response programmatically.

- Expected successful JSON response body:

```json
{
  "original_time": "14:30",
  "formatted_time": "2:30 PM",
  "format": "standard"
}
```

- Example: parsing the response in Python and using values:

```python
import requests

url = "http://localhost:8001/format/standard"
resp = requests.post(url, json={"time": "14:30"}, timeout=5)
resp.raise_for_status()
data = resp.json()

original = data.get("original_time")
fmt = data.get("formatted_time")
print(f"Original: {original} -> Formatted: {fmt}")

# Example check used by automated tests
if fmt and "PM" in fmt:
    print("Received expected formatted time")
else:
    raise SystemExit("Unexpected response format")
```

- Curl output note: `curl` prints the response body to stdout; you can pipe it to a file or a JSON parser for further processing.
