"""Storage Diagnostic Module"""

from typing import Dict, Any, List
from .base import DiagnosticModule
from ..device import DeviceInfo
from ..constants import STORAGE_HEALTHY, STORAGE_MODERATE, STORAGE_CRITICAL


class StorageDiagnostic(DiagnosticModule):
    """Analyze storage usage and provide optimization recommendations"""

    name = "storage"
    description = "Storage usage analysis and optimization"

    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        try:
            domain = 'com.apple.disk_usage'
            total = self._get_device_key(device.udid, 'TotalDiskCapacity', domain=domain)
            free = self._get_device_key(device.udid, 'AmountDataAvailable', domain=domain)
            if not free:
                free = self._get_device_key(device.udid, 'TotalDataAvailable', domain=domain)

            if not total or not free:
                return {"error": "Could not retrieve storage information"}

            total_bytes = int(total)
            free_bytes = int(free)
            used_bytes = total_bytes - free_bytes
            usage_percent = (used_bytes / total_bytes) * 100

            return {
                "total_storage_gb": round(total_bytes / (1024**3), 2),
                "used_storage_gb": round(used_bytes / (1024**3), 2),
                "free_storage_gb": round(free_bytes / (1024**3), 2),
                "usage_percent": round(usage_percent, 2),
                "status": self._get_status(usage_percent),
                "recommendations": self._get_recommendations(usage_percent)
            }
        except Exception as e:
            return {"error": f"Storage diagnostic failed: {str(e)}"}

    def _get_status(self, usage: float) -> str:
        if usage < STORAGE_HEALTHY:
            return "Healthy"
        elif usage < STORAGE_MODERATE:
            return "Moderate"
        elif usage < STORAGE_CRITICAL:
            return "High"
        return "Critical"

    def _get_recommendations(self, usage: float) -> List[str]:
        if usage < STORAGE_HEALTHY:
            return []
        elif usage < STORAGE_MODERATE:
            return ["Review and delete large files", "Enable optimize iPhone storage"]
        else:
            return [
                "Delete unused apps",
                "Clear cache and temporary files",
                "Remove old photos/videos or move to iCloud",
                "Offload unused apps"
            ]
