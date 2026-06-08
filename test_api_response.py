import requests
import json

# Make API request to check compatibility
url = "http://localhost:8000/games/2/compatibility"  # Game ID for Lies of P
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoyMDI2LTA2LTEwfQ.fake"
}

print("Testing API endpoint...")
print(f"URL: {url}")
print("=" * 60)

try:
    # Note: This will fail without valid auth, but we can test manually
    print("\nTo test the actual API:")
    print("1. Open browser dev tools (F12)")
    print("2. Go to Network tab")
    print("3. Click on a game to check compatibility")
    print("4. Look for the request to /games/{id}/compatibility")
    print("5. Check the response - look for 'checks' object with 'os_pass' value")
    print("\nExpected response structure:")
    
    example_response = {
        "checks": {
            "cpu_pass": True,
            "gpu_pass": True,
            "ram_pass": True,
            "storage_pass": True,
            "os_pass": True  # <-- This should be True for Windows 11 vs Windows 10
        },
        "compatibility_percentage": 100,
        "status": "Excellent",
        "minimum_requirements": {
            "operating_system": "Windows 10 64-bit"
        },
        "user_specs": {
            "operating_system": "Windows 11 64-bit"
        }
    }
    
    print(json.dumps(example_response, indent=2))
    
except Exception as e:
    print(f"Error: {e}")
