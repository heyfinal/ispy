"""Battery Diagnostic Module"""

from typing import Dict, Any, List, Optional
from .base import DiagnosticModule
from ..device import DeviceInfo
from ..constants import BATTERY_CYCLE_GOOD, BATTERY_CYCLE_DEGRADED, BATTERY_CYCLE_REPLACE, BATTERY_LOW_LEVEL


class BatteryDiagnostic(DiagnosticModule):
    """Analyze battery health and usage"""

    name = "battery"
    description = "Battery health and cycle analysis"

    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        try:
            battery_level = self._get_device_key(
                device.udid,
                'BatteryCurrentCapacity',
                domain='com.apple.mobile.battery'
            )
            if not battery_level:
                battery_level = self._get_device_key(device.udid, 'BatteryCurrentCapacity')
            cycle_count = self._get_device_key(device.udid, 'BatteryCycleCount')

            level = int(battery_level) if battery_level else None
            cycles = int(cycle_count) if cycle_count else None

            return {
                "battery_level": level,
                "cycle_count": cycles,
                "health_status": self._get_health_status(cycles),
                "recommendations": self._get_recommendations(level, cycles)
            }
        except Exception as e:
            return {"error": f"Battery diagnostic failed: {str(e)}"}

    def _get_health_status(self, cycles: Optional[int]) -> str:
        if cycles is None:
            return "Unknown"
        if cycles < BATTERY_CYCLE_GOOD:
            return "Good"
        elif cycles < BATTERY_CYCLE_DEGRADED:
            return "Fair"
        else:
            return "Degraded"

    def _get_recommendations(self, level: Optional[int], cycles: Optional[int]) -> List[str]:
        recs = []
        if level and level < BATTERY_LOW_LEVEL:
            recs.append("Charge device immediately")
        if cycles:
            if cycles > BATTERY_CYCLE_REPLACE:
                recs.append("Battery replacement strongly recommended")
            elif cycles > BATTERY_CYCLE_DEGRADED:
                recs.append("Consider battery replacement")
                recs.append("Enable optimized battery charging")
        return recs
