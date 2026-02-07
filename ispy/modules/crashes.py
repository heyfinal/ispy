"""Crash Log Diagnostic Module"""

import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import DiagnosticModule
from ..device import DeviceInfo


class CrashDiagnostic(DiagnosticModule):
    """Analyze device crash logs"""

    name = "crashes"
    description = "Crash log analysis"

    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        try:
            if not self._check_tool_available('idevicecrashreport'):
                return {"error": "idevicecrashreport not found. Install libimobiledevice."}

            with tempfile.TemporaryDirectory(prefix="ispy_crash_") as tmp_dir:
                result = subprocess.run(
                    ['idevicecrashreport', '-u', device.udid, '-k', '-e', tmp_dir],
                    capture_output=True, text=True, timeout=90
                )

                if result.returncode != 0:
                    return {
                        "crash_reports_available": False,
                        "error": "Could not retrieve crash reports",
                        "recommendations": ["Ensure device is trusted and connected properly"]
                    }

                crash_files = self._collect_crash_files(Path(tmp_dir))
                if not crash_files:
                    return {
                        "crash_reports_available": False,
                        "total_crash_reports": 0,
                        "recent_crashes_7_days": 0,
                        "crash_summary": {},
                        "top_crashing_apps": [],
                        "recommendations": ["No crash reports found on device"]
                    }

                recent_crashes = self._get_recent_crashes(crash_files, days=7)
                crash_summary = self._summarize_crashes(crash_files)

            return {
                "crash_reports_available": True,
                "total_crash_reports": len(crash_files),
                "recent_crashes_7_days": len(recent_crashes),
                "crash_summary": crash_summary,
                "top_crashing_apps": self._get_top_crashers(crash_files, limit=5),
                "recommendations": self._get_recommendations(crash_files, recent_crashes)
            }
        except subprocess.TimeoutExpired:
            return {"error": "Crash report retrieval timed out"}
        except Exception as e:
            return {"error": f"Crash diagnostic failed: {str(e)}"}

    def _collect_crash_files(self, root: Path) -> List[Dict[str, Any]]:
        crashes = []
        for path in list(root.rglob("*.crash")) + list(root.rglob("*.ips")):
            filename = path.name
            if '-' in filename:
                app_name = filename.split('-')[0]
            else:
                app_name = filename.split('.')[0]

            crashes.append({
                "filename": filename,
                "app_name": app_name,
                "path": str(path)
            })

        return crashes

    def _get_recent_crashes(self, crashes: List[Dict], days: int = 7) -> List[Dict]:
        # Filter recent crashes based on filename date patterns
        recent = []
        cutoff = datetime.now().timestamp() - (days * 86400)

        for crash in crashes:
            # Many crash files have timestamps in filename
            # This is a simplified check
            recent.append(crash)  # Include all for now

        return recent[:50]  # Limit to 50 most recent

    def _summarize_crashes(self, crashes: List[Dict]) -> Dict[str, int]:
        summary = {}
        for crash in crashes:
            app = crash.get('app_name', 'Unknown')
            summary[app] = summary.get(app, 0) + 1
        return summary

    def _get_top_crashers(self, crashes: List[Dict], limit: int = 5) -> List[Dict[str, Any]]:
        summary = self._summarize_crashes(crashes)
        sorted_apps = sorted(summary.items(), key=lambda x: x[1], reverse=True)
        return [{"app": app, "crash_count": count} for app, count in sorted_apps[:limit]]

    def _get_recommendations(self, all_crashes: List, recent: List) -> List[str]:
        recs = []

        if len(recent) > 10:
            recs.append("High number of recent crashes detected")
            recs.append("Consider analyzing crash logs for problematic apps")

        if len(all_crashes) > 50:
            recs.append("Consider clearing old crash reports to free space")

        # Get top crasher
        summary = self._summarize_crashes(all_crashes)
        if summary:
            top_app = max(summary.items(), key=lambda x: x[1])
            if top_app[1] > 5:
                recs.append(f"'{top_app[0]}' has {top_app[1]} crashes - consider reinstalling")

        if not recs:
            recs.append("Crash log analysis complete")

        return recs
