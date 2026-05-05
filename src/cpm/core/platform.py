import platform
from enum import Enum

class Platform(Enum):
    MACOS = "darwin"
    WINDOWS = "windows"
    LINUX = "linux"
    UNKNOWN = "unknown"

def get_current_platform() -> Platform:
    """Detects the current operating system."""
    system = platform.system().lower()
    if system == "darwin":
        return Platform.MACOS
    elif system == "windows":
        return Platform.WINDOWS
    elif system == "linux":
        return Platform.LINUX
    return Platform.UNKNOWN

CURRENT_PLATFORM = get_current_platform()
