"""
iSpy Device - iOS Device Information Models
"""

import subprocess
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class DeviceInfo:
    """Represents an iOS device with its properties"""

    name: str
    model: str
    version: str
    udid: str
    serial: str
    battery_level: Optional[int] = None
    battery_cycle_count: Optional[int] = None
    storage_used: Optional[str] = None
    storage_total: Optional[str] = None
    storage_free: Optional[str] = None
    wifi_address: Optional[str] = None
    bluetooth_address: Optional[str] = None
    hardware_model: Optional[str] = None
    cpu_architecture: Optional[str] = None
    is_supervised: Optional[bool] = None
    activation_state: Optional[str] = None
    last_backup_date: Optional[str] = None
    collected_at: datetime = field(default_factory=datetime.now)

    @property
    def short_udid(self) -> str:
        """Return truncated UDID for display"""
        return f"{self.udid[:8]}..." if len(self.udid) > 8 else self.udid

    @property
    def ios_version(self) -> str:
        """Alias for version field"""
        return self.version

    @property
    def ios_major_version(self) -> int:
        """Extract major iOS version number"""
        try:
            return int(self.version.split('.')[0])
        except (ValueError, IndexError):
            return 0

    @property
    def is_modern_device(self) -> bool:
        """Check if device is considered modern (iOS 15+)"""
        return self.ios_major_version >= 15

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "model": self.model,
            "version": self.version,
            "udid": self.udid,
            "serial": self.serial,
            "battery_level": self.battery_level,
            "battery_cycle_count": self.battery_cycle_count,
            "storage_used": self.storage_used,
            "storage_total": self.storage_total,
            "storage_free": self.storage_free,
            "wifi_address": self.wifi_address,
            "hardware_model": self.hardware_model,
            "cpu_architecture": self.cpu_architecture,
            "is_supervised": self.is_supervised,
            "activation_state": self.activation_state,
            "last_backup_date": self.last_backup_date,
            "collected_at": self.collected_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceInfo":
        """Create DeviceInfo from dictionary"""
        collected_at = data.pop("collected_at", None)
        if collected_at and isinstance(collected_at, str):
            collected_at = datetime.fromisoformat(collected_at)
        else:
            collected_at = datetime.now()

        return cls(**data, collected_at=collected_at)


@dataclass
class DiagnosticResult:
    """Result from a diagnostic module"""

    module_name: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    recommendations: list = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def has_recommendations(self) -> bool:
        return len(self.recommendations) > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "module_name": self.module_name,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp.isoformat(),
        }


def detect_devices() -> List[DeviceInfo]:
    """Detect all connected iOS devices using idevice_id"""
    devices = []

    try:
        # Get list of device UDIDs
        result = subprocess.run(
            ['idevice_id', '-l'],
            capture_output=True, text=True, timeout=10
        )

        if result.returncode != 0 or not result.stdout.strip():
            return devices

        udids = result.stdout.strip().split('\n')

        for udid in udids:
            udid = udid.strip()
            if not udid:
                continue

            device_info = _get_device_info(udid)
            if device_info:
                devices.append(device_info)

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return devices


def _get_device_info(udid: str) -> Optional[DeviceInfo]:
    """Get detailed device information for a UDID"""
    try:
        result = subprocess.run(
            ['ideviceinfo', '-u', udid],
            capture_output=True, text=True, timeout=15
        )

        if result.returncode != 0:
            return None

        # Parse ideviceinfo output
        info = {}
        for line in result.stdout.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip()] = value.strip()

        return DeviceInfo(
            name=info.get('DeviceName', 'Unknown'),
            model=info.get('ProductType', 'Unknown'),
            version=info.get('ProductVersion', 'Unknown'),
            udid=udid,
            serial=info.get('SerialNumber', 'Unknown'),
            battery_level=_parse_int(info.get('BatteryCurrentCapacity')),
            battery_cycle_count=_parse_int(info.get('BatteryCycleCount')),
            wifi_address=info.get('WiFiAddress'),
            bluetooth_address=info.get('BluetoothAddress'),
            hardware_model=info.get('HardwareModel'),
            cpu_architecture=info.get('CPUArchitecture'),
            is_supervised=info.get('IsSupervised') == 'true',
            activation_state=info.get('ActivationState'),
        )

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def _parse_int(value: Optional[str]) -> Optional[int]:
    """Safely parse integer from string"""
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None
