import requests
import json

# Try to get the compatibility report directly from the API
# This assumes you have a session cookie or auth token

# First, let's trace the actual API call
print("=" * 70)
print("CHECKING API RESPONSE FOR OS COMPATIBILITY")
print("=" * 70)

# Read the compatibility service to verify the response structure
with open("app/services/compatibility_service.py", "r") as f:
    content = f.read()
    
# Find the return statement of compute_compatibility_report
import re
match = re.search(r'return \{[\s\S]*?"checks":\s*\{([\s\S]*?)\}', content)
if match:
    print("\n✓ Found checks object in return statement:")
    print("  {")
    for line in match.group(1).split('\n'):
        if line.strip():
            print(f"    {line.strip()}")
    print("  }")
else:
    print("\n❌ Could not find checks object")

print("\n" + "=" * 70)
print("EXPECTED RESPONSE STRUCTURE:")
print("=" * 70)

example = {
    "checks": {
        "cpu_pass": True,
        "gpu_pass": True,
        "ram_pass": True,
        "storage_pass": True,
        "os_pass": True  # <-- Should be here!
    },
    "minimum_requirements": {
        "operating_system": "Windows 10 64-bit"
    },
    "user_specs": {
        "operating_system": "Windows 11 64-bit"
    }
}

print("\nJSON Response should include os_pass:")
print(json.dumps(example, indent=2))

print("\n" + "=" * 70)
print("TO VERIFY IN BROWSER:")
print("=" * 70)
print("""
1. Open DevTools (F12)
2. Go to Network tab
3. Check a game compatibility
4. Click the /games/{id}/compatibility request
5. Go to Response tab
6. Look for "os_pass" in the checks object
7. If it shows: "os_pass": true/false ✓ It's working
8. If it's missing: ❌ Backend hasn't updated
""")
