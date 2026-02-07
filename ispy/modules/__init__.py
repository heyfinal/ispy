"""iSpy Diagnostic Modules"""

from .base import DiagnosticModule, ModuleManager
from .battery import BatteryDiagnostic
from .storage import StorageDiagnostic
from .network import NetworkDiagnostic
from .apps import AppManagementModule
from .security import SecurityDiagnostic
from .performance import PerformanceDiagnostic
from .thermal import ThermalDiagnostic
from .backup import BackupDiagnostic
from .accessibility import AccessibilityDiagnostic
from .crashes import CrashDiagnostic

__all__ = [
    "DiagnosticModule",
    "ModuleManager",
    "BatteryDiagnostic",
    "StorageDiagnostic",
    "NetworkDiagnostic",
    "AppManagementModule",
    "SecurityDiagnostic",
    "PerformanceDiagnostic",
    "ThermalDiagnostic",
    "BackupDiagnostic",
    "AccessibilityDiagnostic",
    "CrashDiagnostic",
]

# Module registry for easy access
AVAILABLE_MODULES = {
    "battery": BatteryDiagnostic,
    "storage": StorageDiagnostic,
    "network": NetworkDiagnostic,
    "apps": AppManagementModule,
    "security": SecurityDiagnostic,
    "performance": PerformanceDiagnostic,
    "thermal": ThermalDiagnostic,
    "backup": BackupDiagnostic,
    "accessibility": AccessibilityDiagnostic,
    "crashes": CrashDiagnostic,
}
