"""App Management Module"""

import csv
import subprocess
from typing import Dict, Any, List
from .base import DiagnosticModule
from ..device import DeviceInfo
from ..constants import APP_COUNT_HIGH


class AppManagementModule(DiagnosticModule):
    """Comprehensive app analysis"""

    name = "apps"
    description = "Installed applications analysis"

    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        try:
            if not self._check_tool_available('ideviceinstaller'):
                return {"error": "ideviceinstaller not found. Install libimobiledevice."}

            result = self._run_list_command(['ideviceinstaller', '-u', device.udid, 'list', '--user'])
            if result.returncode != 0:
                # Fallback for older ideviceinstaller versions
                result = self._run_list_command(['ideviceinstaller', '-u', device.udid, 'list'])
            if result.returncode != 0:
                result = self._run_list_command(['ideviceinstaller', '-u', device.udid, '-l'])

            if result.returncode != 0:
                stderr = (result.stderr or "").strip()
                hint = "Ensure the device is unlocked and trusted."
                return {"error": f"Failed to get app list. {hint} {stderr}".strip()}

            apps = []
            lines = [line for line in result.stdout.splitlines() if line.strip()]
            if not lines:
                return {"error": "No apps returned by ideviceinstaller"}

            reader = csv.reader(lines)
            header = next(reader, None)
            for row in reader:
                if not row:
                    continue
                bundle_id = row[0].strip() if len(row) > 0 else ""
                name = row[2].strip().strip('"') if len(row) > 2 else ""
                if bundle_id:
                    apps.append({"bundle_id": bundle_id, "name": name or bundle_id})

            apps.sort(key=lambda x: x.get('name', '').lower())

            return {
                "total_apps": len(apps),
                "apps": apps[:25],  # First 25 alphabetically
                "recommendations": self._get_recommendations(apps)
            }
        except Exception as e:
            return {"error": f"App management failed: {str(e)}"}

    def _run_list_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    def _get_recommendations(self, apps: List[Dict]) -> List[str]:
        recs = []
        if len(apps) > APP_COUNT_HIGH:
            recs.append("Consider removing unused apps to free storage")
        return recs
