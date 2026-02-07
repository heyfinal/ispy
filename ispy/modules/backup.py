"""Backup Diagnostic Module"""

import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional
from .base import DiagnosticModule
from ..device import DeviceInfo


class BackupDiagnostic(DiagnosticModule):
    """Analyze device backup status"""

    name = "backup"
    description = "Backup status and recommendations"

    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        try:
            # Check backup-related info
            last_backup = self._get_device_key(device.udid, 'LastBackupDate')
            backup_enabled = self._get_device_key(device.udid, 'BackupEnabled')
            cloud_backup = self._get_device_key(device.udid, 'CloudBackupEnabled')

            last_backup_date = None
            days_since_backup = None

            if last_backup:
                try:
                    # Parse ISO format date
                    last_backup_date = datetime.fromisoformat(last_backup.replace('Z', '+00:00'))
                    days_since_backup = (datetime.now(last_backup_date.tzinfo) - last_backup_date).days
                except (ValueError, TypeError):
                    pass

            backup_status = self._get_backup_status(days_since_backup, cloud_backup)

            return {
                "last_backup_date": last_backup_date.isoformat() if last_backup_date else None,
                "days_since_backup": days_since_backup,
                "backup_enabled": backup_enabled == 'true' if backup_enabled else None,
                "cloud_backup_enabled": cloud_backup == 'true' if cloud_backup else None,
                "status": backup_status,
                "recommendations": self._get_recommendations(days_since_backup, cloud_backup)
            }
        except Exception as e:
            return {"error": f"Backup diagnostic failed: {str(e)}"}

    def _get_backup_status(self, days: Optional[int], cloud: Optional[str]) -> str:
        if days is None:
            return "Unknown"

        if days <= 1:
            return "Current"
        elif days <= 7:
            return "Recent"
        elif days <= 30:
            return "Outdated"
        else:
            return "Critical"

    def _get_recommendations(self, days: Optional[int], cloud: Optional[str]) -> List[str]:
        recs = []

        if days is None:
            recs.append("Unable to determine backup status - verify backup configuration")
            recs.append("Enable iCloud backup or perform manual backup via Finder/iTunes")
        elif days > 30:
            recs.extend([
                f"Last backup was {days} days ago - backup immediately",
                "Enable automatic iCloud backup",
                "Connect to WiFi and power to trigger backup"
            ])
        elif days > 7:
            recs.extend([
                f"Last backup was {days} days ago",
                "Consider enabling automatic daily backups",
                "Ensure device connects to WiFi regularly"
            ])
        elif days > 1:
            recs.append("Backup is recent but consider daily backups for important data")

        if cloud and cloud != 'true':
            recs.append("Enable iCloud backup for automatic protection")

        if not recs:
            recs.append("Backup status is healthy")

        return recs
