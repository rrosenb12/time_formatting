# Time Formatting API

A FastAPI microservice that formats times and provides a simple HTTP API. This README now includes the communication contract required by the assignment: how to programmatically request data, how the service responds, an example test program, and an example UML sequence diagram placeholder.

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

## Requesting Data (examples)

These examples show how a client program should *request* time-formatting from the service.

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
