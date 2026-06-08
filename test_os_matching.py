from app.data.os_benchmarks import OS_BENCHMARKS

def get_os_score(os_name: str) -> int:
    os_name = (os_name or "").lower()
    print(f"  Checking OS: '{os_name}'")
    
    for os, score in OS_BENCHMARKS.items():
        if os in os_name:
            print(f"    ✓ Matched '{os}' → Score: {score}")
            return score
    
    print(f"    ✗ No match found → Score: 0")
    return 0

# Test cases
test_cases = [
    "Windows 10 64-bit",
    "Windows 11",
    "Ubuntu 20.04",
    "macOS 12",
    None,
    "",
]

print("=== Testing OS Score Matching ===\n")
for test in test_cases:
    print(f"Input: {test}")
    score = get_os_score(test)
    print(f"Result: {score}\n")
