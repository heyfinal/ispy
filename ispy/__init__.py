"""
iSpy - Advanced iOS Diagnostic & Management Tool
A comprehensive iOS device analysis and troubleshooting toolkit with AI integration
"""

__version__ = "2.0.0"
__author__ = "Daniel"

from .core import iSpyTool
from .device import DeviceInfo
from .ai_engine import AIEngine
from .config import Config
from .health import HealthScore

__all__ = [
    "iSpyTool",
    "DeviceInfo",
    "AIEngine",
    "Config",
    "HealthScore",
    "__version__",
]
