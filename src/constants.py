"""
Application-wide constants.

This module provides shared constants for time conversion and terminal output
formatting used across the TimeRecorder application.
"""

import colorama

colorama.init(autoreset=True)

# Time conversion (seconds per unit)
SEC_IN_MIN = 60
SEC_IN_HOUR = 3600
MIN_IN_HOUR = 60

# Terminal colors (overtime=green, undertime=red)
RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
RESET = colorama.Style.RESET_ALL
