"""Performance Diagnostic Module"""

import subprocess
from typing import Dict, Any, List, Optional
from .base import DiagnosticModule
from ..device import DeviceInfo


class PerformanceDiagnostic(DiagnosticModule):
    """Analyze device performance metrics"""

    name = "performance"
    description = "Performance and resource usage analysis"

    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        try:
            # Get hardware info for performance context
            cpu_arch = self._get_device_key(device.udid, 'CPUArchitecture')
            hw_model = self._get_device_key(device.udid, 'HardwareModel')

            # Memory info
            total_ram = self._get_device_key(device.udid, 'TotalSystemCapacity')

            # Uptime (if available)
            uptime = self._get_device_key(device.udid, 'UpTime')

            performance_rating = self._calculate_performance_rating(
                device.model,
                cpu_arch,
                total_ram
            )

            return {
                "cpu_architecture": cpu_arch,
                "hardware_model": hw_model,
                "total_ram_bytes": int(total_ram) if total_ram else None,
                "total_ram_gb": round(int(total_ram) / (1024**3), 2) if total_ram else None,
                "uptime_seconds": int(uptime) if uptime else None,
                "performance_rating": performance_rating,
                "recommendations": self._get_recommendations(performance_rating, uptime)
            }
        except Exception as e:
            return {"error": f"Performance diagnostic failed: {str(e)}"}

    def _calculate_performance_rating(
        self,
        model: Optional[str],
        cpu_arch: Optional[str],
        ram: Optional[str]
    ) -> str:
        score = 0

        # CPU architecture scoring
        if cpu_arch:
            if 'arm64e' in cpu_arch.lower():
                score += 40
            elif 'arm64' in cpu_arch.lower():
                score += 30
            else:
                score += 10

        # RAM scoring
        if ram:
            try:
                ram_gb = int(ram) / (1024**3)
                if ram_gb >= 8:
                    score += 40
                elif ram_gb >= 6:
                    score += 30
                elif ram_gb >= 4:
                    score += 20
                else:
                    score += 10
            except (ValueError, TypeError):
                pass

        # Model-based scoring (newer models)
        if model:
            model_lower = model.lower()
            if any(x in model_lower for x in ['15', '16', '17']):
                score += 20
            elif any(x in model_lower for x in ['13', '14']):
                score += 15
            elif any(x in model_lower for x in ['11', '12']):
                score += 10

        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Moderate"
        else:
            return "Limited"

    def _get_recommendations(self, rating: str, uptime: Optional[str]) -> List[str]:
        recs = []

        if rating == "Limited":
            recs.append("Consider upgrading to a newer device for better performance")
            recs.append("Close unused apps to free memory")
            recs.append("Disable background app refresh for non-essential apps")

        if rating == "Moderate":
            recs.append("Close background apps when not in use")
            recs.append("Restart device periodically to clear memory")

        # Uptime recommendation
        if uptime:
            try:
                uptime_days = int(uptime) / 86400
                if uptime_days > 14:
                    recs.append(f"Device uptime is {int(uptime_days)} days - consider restarting")
            except (ValueError, TypeError):
                pass

        if not recs:
            recs.append("Performance metrics look healthy")

        return recs
