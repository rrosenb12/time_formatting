# Time Formatting API

A FastAPI microservice that formats times and provides a simple HTTP API. This README now includes the communication contract required by the assignment: how to programmatically request data, how the service responds, an example test program, and an example UML sequence diagram placeholder.

## Features

- Format a 24-hour `HH:MM` time string to a 12-hour standard time (AM/PM).
- Simple JSON-based HTTP API.

## Service Endpoints (Contract)

- **Health check**: `GET /health`
  - Response: `200 OK`, body: `{ "status": "ok" }`

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

- **List timezones (optional helper)**: `GET /timezones`
  - Response: JSON list of supported timezone strings (if implemented).

IMPORTANT: This is the communication contract. Do not change request/response shapes without coordinating with your teammates.

## Example Requests

Standard time formatting (curl):

```powershell
curl -X POST "http://localhost:8001/format/standard" `
  -H "Content-Type: application/json" `
  -d '{"time": "14:30"}'
```

Equivalent example using Python `requests`:

```python
import requests

url = "http://localhost:8001/format/standard"
resp = requests.post(url, json={"time": "14:30"}, timeout=5)
resp.raise_for_status()
data = resp.json()
print(data)
# Expected: {'original_time':'14:30','formatted_time':'2:30 PM','format':'standard'}
```

## Test Program (example)

Create a small test program to demonstrate the contract. Example file: `test_format.py` (this file is an example; add to repo if you want a runnable test)

```python
#!/usr/bin/env python3
"""Simple test program that calls the time-formatting microservice."""
import requests
import sys

def test(time_str="14:30"):
    url = "http://localhost:8001/format/standard"
    try:
        r = requests.post(url, json={"time": time_str}, timeout=5)
        r.raise_for_status()
    except Exception as e:
        print("Request failed:", e)
        return 2
    data = r.json()
    print("Request:", time_str)
    print("Response:", data)
    if data.get("formatted_time"):
        return 0
    return 1

if __name__ == '__main__':
    sys.exit(test(sys.argv[1]) if len(sys.argv) > 1 else test())
```

This test program demonstrates programmatic request and response handling (one of the assignment requirements). It can be run with:

```powershell
python test_format.py 14:30
```

or simply `python test_format.py` to use the default example time.

## UML Sequence Diagram (communication example)

Include a UML sequence diagram in this README (or as an image file in the repo) showing the interactions below. A simple ASCII/PlantUML placeholder is provided here; replace with a proper diagram in your submission.

PlantUML example (paste to an online PlantUML editor or save as `.puml`):

```text
@startuml
actor TestProgram
participant TimeFormattingService

TestProgram -> TimeFormattingService: POST /format/standard { "time": "14:30" }
activate TimeFormattingService
TimeFormattingService -> TimeFormattingService: validate input
TimeFormattingService -> TimeFormattingService: format time
TimeFormattingService -> TestProgram: 200 OK \n{ "original_time":"14:30","formatted_time":"2:30 PM","format":"standard" }
deactivate TimeFormattingService
@enduml
```

Guidance: Your UML should clearly show the calling program (test program), the HTTP request to `/format/standard`, internal validation/formatting actions (optional), and the JSON response returned.

## Setup & Run (quick)

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Run the service (example using `uvicorn`):

```powershell
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

3. Run the test program (from repo root or where `test_format.py` is saved):

```powershell
python test_format.py 14:30
```

## Assignment Requirements Checklist

- **One test program**: The `test_format.py` example shows how to programmatically request and receive data.
- **Communication contract**: The `POST /format/standard` request/response shapes are documented above — include these in your submission and do not change them without coordination.
- **UML sequence diagram**: PlantUML placeholder provided; include a final diagram image or `.puml` file in your repo.

## Notes for teammates / graders

- Keep this communication contract stable during integration sprints.
- If you add or change endpoints, update this README and notify the team. The grader expects the README to contain an example call, an example response, and a UML diagram.

If you'd like, I can also create an actual `test_format.py` file in the `time_formatting/` folder and add a `diagram.puml` image placeholder — tell me if you want those files added.

