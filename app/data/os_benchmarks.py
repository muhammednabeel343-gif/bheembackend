OS_BENCHMARKS = {
    # Windows - specific versions checked first
    "windows 11": 100,
    "windows 10": 80,
    "windows 8.1": 60,
    "windows 8": 50,
    "windows 7": 40,
    "windows vista": 20,
    "windows xp": 10,
    # Windows - generic fallback (assumes modern/current version)
    "windows": 100,
    # Ubuntu - specific versions checked first
    "ubuntu 22.04": 90,
    "ubuntu 20.04": 85,
    "ubuntu 22": 90,
    "ubuntu 20": 85,
    # Ubuntu - generic fallback
    "ubuntu": 90,
    "linux": 85,
    # macOS - specific versions checked first
    "macos 14": 95,
    "macos 13": 90,
    "macos 12": 85,
    # macOS - generic fallback
    "macos": 95,
    "mac": 95,
}
