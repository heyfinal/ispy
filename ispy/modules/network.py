"""Network Diagnostic Module"""

from typing import Dict, Any, List
from .base import DiagnosticModule
from ..device import DeviceInfo


class NetworkDiagnostic(DiagnosticModule):
    """Analyze network connectivity"""

    name = "network"
    description = "Network connectivity analysis"

    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        try:
            wifi_addr = self._get_device_key(device.udid, 'WiFiAddress')
            carrier = self._get_device_key(device.udid, 'CarrierSettingsVersion')

            wifi_connected = bool(wifi_addr)
            has_cellular = bool(carrier)

            return {
                "wifi_connected": wifi_connected,
                "wifi_address": wifi_addr if wifi_connected else None,
                "has_cellular": has_cellular,
                "connectivity_status": "Connected" if (wifi_connected or has_cellular) else "Disconnected",
                "recommendations": self._get_recommendations(wifi_connected, has_cellular)
            }
        except Exception as e:
            return {"error": f"Network diagnostic failed: {str(e)}"}

    def _get_recommendations(self, wifi: bool, cellular: bool) -> List[str]:
        recs = []
        if not wifi and not cellular:
            recs.extend([
                "Check WiFi settings",
                "Verify cellular data is enabled",
                "Reset network settings if issues persist"
            ])
        elif not wifi:
            recs.append("Connect to WiFi to save cellular data")
        return recs
