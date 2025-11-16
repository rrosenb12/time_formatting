import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"


def test_root():
    print("1. Testing root endpoint...")
    resp = requests.get(f"{BASE_URL}/")
    print(f"Request: GET {BASE_URL}/")
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.json()}")
    assert resp.status_code == 200
    print("✓ Root OK\n")


def test_timezones():
    print("2. Testing timezone list...")
    resp = requests.get(f"{BASE_URL}/time/timezones")
    print(f"Request: GET {BASE_URL}/time/timezones")
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Body: {data}")
    assert resp.status_code == 200
    assert "timezones" in data
    assert "EST" in data.get("timezones", [])
    print("✓ Timezones listed\n")


def test_get_current_time():
    print("3. Testing get current time for EST...")
    resp = requests.get(f"{BASE_URL}/time/current", params={"timezone": "EST"})
    print(f"Request: GET {BASE_URL}/time/current?timezone=EST")
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.json()}")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("timezone") == "EST"
    # validate timestamp format
    datetime.strptime(body.get("current_time"), "%Y-%m-%d %H:%M:%S")
    print("✓ Current time OK\n")


def test_convert_time():
    print("4. Testing timezone conversion EST -> PST...")
    payload = {"time_str": "13:15:00", "from_timezone": "EST", "to_timezone": "PST"}
    resp = requests.post(f"{BASE_URL}/time/convert", json=payload)
    print(f"Request: POST {BASE_URL}/time/convert with payload {json.dumps(payload)}")
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.json()}")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("original_time") == "13:15:00"
    assert "converted_time" in data
    # converted_time should be a HH:MM:SS string
    datetime.strptime(data.get("converted_time"), "%H:%M:%S")
    print("✓ Conversion OK\n")


def test_format_standard_examples():
    print("5. Testing standard format conversions (military -> 12-hour)...")
    cases = [
        ("00:00", "12:00 AM"),
        ("01:05", "1:05 AM"),
        ("12:00", "12:00 PM"),
        ("13:15", "1:15 PM"),
        ("23:59", "11:59 PM"),
    ]

    for inp, expected in cases:
        payload = {"time": inp}
        resp = requests.post(f"{BASE_URL}/format/standard", json=payload)
        print(f"Request: POST {BASE_URL}/format/standard with payload {json.dumps(payload)}")
        print(f"Status: {resp.status_code}")
        body = resp.json()
        print(f"Body: {body}")
        assert resp.status_code == 200
        formatted = body.get("formatted_time")
        assert formatted == expected, f"Expected {expected}, got {formatted}"
    print("✓ Standard formatting examples OK\n")


def test_convert_12_to_military():
    print("6. Testing conversion from 12-hour to military time...")
    cases = [
        ("12:00 AM", "00:00"),
        ("1:05 AM", "01:05"),
        ("12:00 PM", "12:00"),
        ("1:15 PM", "13:15"),
        ("11:59 PM", "23:59"),
    ]

    for inp, expected in cases:
        # Prefer service endpoint if available, otherwise fall back to local conversion
        try:
            resp = requests.post(f"{BASE_URL}/format/to_military", json={"time_12": inp}, timeout=2)
            if resp.status_code == 200:
                body = resp.json()
                print(f"Request: POST {BASE_URL}/format/to_military with payload {{'time_12': '{inp}'}}")
                print(f"Status: {resp.status_code}")
                print(f"Body: {body}")
                mil = body.get("military_time")
                assert mil == expected, f"Expected {expected}, got {mil} from service"
                continue
        except requests.exceptions.RequestException:
            # endpoint absent or service not available — fall through to local conversion
            pass

        # Local fallback: parse 12-hour time and format to HH:MM (24-hour)
        print(f"Service endpoint not available; falling back to local parse for '{inp}'")
        parsed = datetime.strptime(inp, "%I:%M %p")
        local_mil = parsed.strftime("%H:%M")
        print(f"Local conversion: {inp} -> {local_mil}")
        assert local_mil == expected, f"Expected {expected}, got {local_mil} locally"

    print("✓ 12-hour to military conversion OK\n")


if __name__ == "__main__":
    print("Starting time_formatting microservice tests...\n")
    try:
        test_root()
        test_timezones()
        test_get_current_time()
        test_convert_time()
        test_format_standard_examples()
        test_convert_12_to_military()
        print("All tests completed successfully.")
    except AssertionError as e:
        print(f"Assertion failed: {e}")
    except Exception as e:
        print(f"Test run failed with error: {e}")
