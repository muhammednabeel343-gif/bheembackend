from app.data.os_benchmarks import OS_BENCHMARKS

def get_os_score(os_name: str) -> int:
    os_name = (os_name or "").lower()
    for os, score in OS_BENCHMARKS.items():
        if os in os_name:
            return score
    return 0

def check_os_compatibility(required_os: str, user_os: str) -> bool:
    """
    Check if user's OS is compatible with the game's required OS.
    """
    # If no OS requirement, always compatible
    if not required_os:
        return True
    
    required_os_lower = (required_os or "").lower()
    user_os_lower = (user_os or "").lower()
    
    # Extract OS family
    def get_os_family(os_str):
        if "windows" in os_str:
            return "windows"
        elif "ubuntu" in os_str or "linux" in os_str:
            return "linux"
        elif "mac" in os_str:
            return "macos"
        return None
    
    required_family = get_os_family(required_os_lower)
    user_family = get_os_family(user_os_lower)
    
    # If different OS families, not compatible
    if required_family and user_family and required_family != user_family:
        return False
    
    # Same family or unknown - check score comparison
    required_score = get_os_score(required_os)
    user_score = get_os_score(user_os)
    
    # Within same family, higher or equal score means compatible
    return user_score >= required_score

# Test cases
test_cases = [
    ("Windows 10", "Windows 11", True, "Win11 → Win10 (forward compatible)"),
    ("Windows 11", "Windows 10", False, "Win10 → Win11 (not backward compatible)"),
    ("Windows 10", "Ubuntu 20.04", False, "Ubuntu → Windows (different families)"),
    ("Ubuntu 20.04", "Ubuntu 22.04", True, "Ubuntu22 → Ubuntu20 (forward compatible)"),
    ("macOS 12", "macOS 14", True, "macOS14 → macOS12 (forward compatible)"),
    ("Windows 10 64-bit", "Windows 11", True, "Windows with suffix"),
    (None, "Windows 10", True, "No OS requirement"),
    ("", "Windows 10", True, "Empty OS requirement"),
]

print("=== OS Compatibility Tests ===\n")
for required, user, expected, description in test_cases:
    result = check_os_compatibility(required, user)
    status = "✓" if result == expected else "✗"
    print(f"{status} {description}")
    print(f"   Required: {required} | User: {user}")
    print(f"   Result: {result} (Expected: {expected})\n")
