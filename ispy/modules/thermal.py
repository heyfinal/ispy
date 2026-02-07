"""Thermal Diagnostic Module"""

from typing import Dict, Any, List, Optional
from .base import DiagnosticModule
from ..device import DeviceInfo
from ..constants import TEMP_NORMAL, TEMP_WARNING, TEMP_CRITICAL


class ThermalDiagnostic(DiagnosticModule):
    """Monitor device thermal state"""

    name = "thermal"
    description = "Thermal state monitoring"

    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        try:
            # Thermal state from device
            thermal_state = self._get_device_key(device.udid, 'ThermalState')

            # Battery temperature (indirect thermal indicator)
            battery_temp = self._get_device_key(device.udid, 'BatteryTemperature')

            temp_celsius = None
            if battery_temp:
                try:
                    # Battery temp often in centigrade * 100
                    temp_celsius = float(battery_temp) / 100
                except (ValueError, TypeError):
                    pass

            status = self._get_thermal_status(thermal_state, temp_celsius)

            return {
                "thermal_state": thermal_state or "Unknown",
                "battery_temperature_c": round(temp_celsius, 1) if temp_celsius else None,
                "battery_temperature_f": round((temp_celsius * 9/5) + 32, 1) if temp_celsius else None,
                "status": status,
                "recommendations": self._get_recommendations(status, temp_celsius)
            }
        except Exception as e:
            return {"error": f"Thermal diagnostic failed: {str(e)}"}

    def _get_thermal_status(self, state: Optional[str], temp: Optional[float]) -> str:
        # Check explicit thermal state first
        if state:
            state_lower = state.lower()
            if 'critical' in state_lower or 'hot' in state_lower:
                return "Critical"
            elif 'warning' in state_lower or 'warm' in state_lower:
                return "Warning"
            elif 'nominal' in state_lower or 'normal' in state_lower:
                return "Normal"

        # Fall back to temperature-based assessment
        if temp is not None:
            if temp >= TEMP_CRITICAL:
                return "Critical"
            elif temp >= TEMP_WARNING:
                return "Warning"
            elif temp <= TEMP_NORMAL:
                return "Normal"
            else:
                return "Elevated"

        return "Unknown"

    def _get_recommendations(self, status: str, temp: Optional[float]) -> List[str]:
        recs = []

        if status == "Critical":
            recs.extend([
                "Stop using device immediately and let it cool down",
                "Remove device from case",
                "Move to cooler environment",
                "Close all apps and disable location services temporarily"
            ])
        elif status == "Warning":
            recs.extend([
                "Reduce device usage intensity",
                "Close resource-intensive apps",
                "Avoid charging while using heavy apps",
                "Remove case if overheating persists"
            ])
        elif status == "Elevated":
            recs.append("Monitor temperature - slight elevation is normal during heavy use")

        if not recs:
            recs.append("Thermal state is normal")

        return recs
