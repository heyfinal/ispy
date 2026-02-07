"""
iSpy Constants - Centralized configuration values
"""

# Battery Health Thresholds
BATTERY_CYCLE_GOOD = 500
BATTERY_CYCLE_DEGRADED = 800
BATTERY_CYCLE_REPLACE = 1000
BATTERY_LOW_LEVEL = 20

# Storage Thresholds (percentage)
STORAGE_HEALTHY = 70
STORAGE_MODERATE = 85
STORAGE_CRITICAL = 90

# Temperature Thresholds (Celsius)
TEMP_NORMAL = 40
TEMP_WARM = 45
TEMP_WARNING = 45  # Alias for TEMP_WARM
TEMP_HOT = 50
TEMP_CRITICAL = 55

# Performance Thresholds
MEMORY_LOW_GB = 2
MEMORY_MEDIUM_GB = 4

# Security Score Weights
SECURITY_PASSCODE_WEIGHT = 40
SECURITY_ACTIVATION_WEIGHT = 30
SECURITY_SUPERVISED_WEIGHT = 30

# AI Configuration
AI_DEFAULT_MODEL = "gpt-4o-mini"
AI_MAX_LOG_CHARS = 4000
AI_MAX_TOKENS = 500
AI_MAX_CONTEXT_CHARS = 12000

# Health Score Weights
HEALTH_BATTERY_WEIGHT = 0.25
HEALTH_STORAGE_WEIGHT = 0.20
HEALTH_PERFORMANCE_WEIGHT = 0.20
HEALTH_SECURITY_WEIGHT = 0.15
HEALTH_THERMAL_WEIGHT = 0.10
HEALTH_BACKUP_WEIGHT = 0.10

# Supported iPhone Models (for performance rating)
HIGH_PERFORMANCE_MODELS = ["iPhone12", "iPhone13", "iPhone14", "iPhone15", "iPhone16"]
MEDIUM_PERFORMANCE_MODELS = ["iPhone8", "iPhone9", "iPhone10", "iPhone11", "iPhoneX"]

# File Paths
DEFAULT_CONFIG_DIR = "~/.ispy"
DEFAULT_LOG_FILE = "ispy.log"
DEFAULT_DATA_DIR = "data"
DEFAULT_BACKUP_ROOT = "~/Library/Application Support/MobileSync/Backup"

# Thermal State Mappings
THERMAL_STATE_TEMPS = {
    "Normal": 35,
    "Fair": 42,
    "Serious": 48,
    "Critical": 55,
    "Unknown": 40,
}

# App thresholds
APP_COUNT_HIGH = 100
APP_COUNT_WARNING = 150
