#!/usr/bin/env python3
"""
iSpy - Advanced iOS Diagnostic & Management Tool
A comprehensive iOS device analysis and troubleshooting toolkit with AI integration
"""

import os
import sys
import json
import subprocess
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import requests
import openai
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import print as rprint

# Import analytics module
try:
    from modules.advanced_analytics import DeviceAnalytics
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

console = Console()

@dataclass
class DeviceInfo:
    name: str
    model: str
    version: str
    udid: str
    serial: str
    battery_level: Optional[int] = None
    storage_used: Optional[str] = None
    storage_total: Optional[str] = None

class AIEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
    
    def analyze_logs(self, logs: str, context: str = "") -> Dict[str, Any]:
        """AI-powered log analysis"""
        try:
            prompt = f"""
            Analyze the following iOS device logs and provide insights:
            
            Context: {context}
            
            Logs:
            {logs[:2000]}  # Truncate for API limits
            
            Please provide:
            1. Summary of issues found
            2. Severity level (Low/Medium/High/Critical)
            3. Recommended actions
            4. Potential root causes
            
            Format as JSON.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": f"AI analysis failed: {str(e)}"}
    
    def suggest_solution(self, problem: str, device_info: DeviceInfo) -> str:
        """Get AI-powered solution suggestions"""
        try:
            prompt = f"""
            iOS troubleshooting request:
            Problem: {problem}
            Device: {device_info.model}
            iOS Version: {device_info.version}
            
            Provide step-by-step troubleshooting instructions.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"AI suggestion failed: {str(e)}"

class ModuleManager:
    def __init__(self):
        self.modules = {}
        self.module_dir = Path(__file__).parent / "modules"
        self.module_dir.mkdir(exist_ok=True)
    
    def register_module(self, name: str, module_class):
        """Register a diagnostic module"""
        self.modules[name] = module_class
    
    def get_available_modules(self) -> List[str]:
        """Get list of available modules"""
        return list(self.modules.keys())
    
    def run_module(self, name: str, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        """Execute a specific module"""
        if name not in self.modules:
            return {"error": f"Module '{name}' not found"}
        
        try:
            module = self.modules[name]()
            return module.run(device, **kwargs)
        except Exception as e:
            return {"error": f"Module execution failed: {str(e)}"}

class DiagnosticModule:
    """Base class for diagnostic modules"""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

class BatteryDiagnostic(DiagnosticModule):
    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        """Analyze battery health and usage"""
        try:
            # Get battery info using ideviceinfo
            result = subprocess.run([
                'ideviceinfo', '-u', device.udid, '-k', 'BatteryCurrentCapacity'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                battery_level = int(result.stdout.strip())
                
                # Get battery cycle count
                cycle_result = subprocess.run([
                    'ideviceinfo', '-u', device.udid, '-k', 'BatteryCycleCount'
                ], capture_output=True, text=True)
                
                cycle_count = int(cycle_result.stdout.strip()) if cycle_result.returncode == 0 else None
                
                return {
                    "battery_level": battery_level,
                    "cycle_count": cycle_count,
                    "health_status": "Good" if cycle_count and cycle_count < 500 else "Degraded",
                    "recommendations": self._get_battery_recommendations(battery_level, cycle_count)
                }
        except Exception as e:
            return {"error": f"Battery diagnostic failed: {str(e)}"}
    
    def _get_battery_recommendations(self, level: int, cycles: Optional[int]) -> List[str]:
        recommendations = []
        
        if level < 20:
            recommendations.append("Charge device immediately")
        
        if cycles and cycles > 500:
            recommendations.append("Consider battery replacement")
            recommendations.append("Enable optimized battery charging")
        
        if cycles and cycles > 1000:
            recommendations.append("Battery replacement strongly recommended")
        
        return recommendations

class StorageDiagnostic(DiagnosticModule):
    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        """Analyze storage usage and optimize"""
        try:
            # Get storage info
            total_result = subprocess.run([
                'ideviceinfo', '-u', device.udid, '-k', 'TotalDiskCapacity'
            ], capture_output=True, text=True)
            
            free_result = subprocess.run([
                'ideviceinfo', '-u', device.udid, '-k', 'AmountDataAvailable'
            ], capture_output=True, text=True)
            
            if total_result.returncode == 0 and free_result.returncode == 0:
                total_bytes = int(total_result.stdout.strip())
                free_bytes = int(free_result.stdout.strip())
                used_bytes = total_bytes - free_bytes
                
                total_gb = total_bytes / (1024**3)
                free_gb = free_bytes / (1024**3)
                used_gb = used_bytes / (1024**3)
                usage_percent = (used_bytes / total_bytes) * 100
                
                return {
                    "total_storage_gb": round(total_gb, 2),
                    "used_storage_gb": round(used_gb, 2),
                    "free_storage_gb": round(free_gb, 2),
                    "usage_percent": round(usage_percent, 2),
                    "status": self._get_storage_status(usage_percent),
                    "recommendations": self._get_storage_recommendations(usage_percent)
                }
        except Exception as e:
            return {"error": f"Storage diagnostic failed: {str(e)}"}
    
    def _get_storage_status(self, usage_percent: float) -> str:
        if usage_percent < 70:
            return "Healthy"
        elif usage_percent < 85:
            return "Moderate"
        else:
            return "Critical"
    
    def _get_storage_recommendations(self, usage_percent: float) -> List[str]:
        recommendations = []
        
        if usage_percent > 85:
            recommendations.extend([
                "Delete unused apps",
                "Clear cache and temporary files",
                "Remove old photos/videos",
                "Offload unused apps"
            ])
        elif usage_percent > 70:
            recommendations.extend([
                "Review and delete large files",
                "Enable optimize iPhone storage"
            ])
        
        return recommendations

class NetworkDiagnostic(DiagnosticModule):
    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        """Analyze network connectivity and performance"""
        try:
            # Check WiFi status
            wifi_result = subprocess.run([
                'ideviceinfo', '-u', device.udid, '-k', 'WiFiAddress'
            ], capture_output=True, text=True)
            
            # Check cellular info if available
            carrier_result = subprocess.run([
                'ideviceinfo', '-u', device.udid, '-k', 'CarrierSettingsVersion'
            ], capture_output=True, text=True)
            
            wifi_connected = wifi_result.returncode == 0 and wifi_result.stdout.strip()
            has_cellular = carrier_result.returncode == 0
            
            return {
                "wifi_connected": wifi_connected,
                "wifi_address": wifi_result.stdout.strip() if wifi_connected else None,
                "has_cellular": has_cellular,
                "connectivity_status": "Connected" if wifi_connected or has_cellular else "Disconnected",
                "recommendations": self._get_network_recommendations(wifi_connected, has_cellular)
            }
        except Exception as e:
            return {"error": f"Network diagnostic failed: {str(e)}"}
    
    def _get_network_recommendations(self, wifi: bool, cellular: bool) -> List[str]:
        recommendations = []
        
        if not wifi and not cellular:
            recommendations.extend([
                "Check WiFi settings",
                "Verify cellular data is enabled",
                "Reset network settings if issues persist"
            ])
        elif not wifi:
            recommendations.append("Connect to WiFi to save cellular data")
        
        return recommendations

class AppManagementModule(DiagnosticModule):
    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        """Comprehensive app analysis and management"""
        try:
            # Get installed apps
            apps_result = subprocess.run([
                'ideviceinstaller', '-u', device.udid, '-l'
            ], capture_output=True, text=True)
            
            if apps_result.returncode != 0:
                return {"error": "Failed to get app list"}
            
            apps = []
            for line in apps_result.stdout.split('\n'):
                if ' - ' in line:
                    bundle_id, name = line.split(' - ', 1)
                    apps.append({
                        "bundle_id": bundle_id.strip(),
                        "name": name.strip(),
                        "size": self._get_app_size(device.udid, bundle_id.strip())
                    })
            
            # Sort by size
            apps.sort(key=lambda x: x.get('size', 0), reverse=True)
            
            total_size = sum(app.get('size', 0) for app in apps)
            
            return {
                "total_apps": len(apps),
                "apps": apps[:20],  # Top 20 largest apps
                "total_app_size_mb": round(total_size / (1024*1024), 2),
                "recommendations": self._get_app_recommendations(apps)
            }
        except Exception as e:
            return {"error": f"App management failed: {str(e)}"}
    
    def _get_app_size(self, udid: str, bundle_id: str) -> int:
        """Get app size in bytes"""
        try:
            result = subprocess.run([
                'ideviceinstaller', '-u', udid, '-l', '-o', 'list_user'
            ], capture_output=True, text=True)
            # This is a simplified version - real implementation would parse app info
            return 0
        except:
            return 0
    
    def _get_app_recommendations(self, apps: List[Dict]) -> List[str]:
        recommendations = []
        
        if len(apps) > 100:
            recommendations.append("Consider removing unused apps to free storage")
        
        large_apps = [app for app in apps if app.get('size', 0) > 500*1024*1024]  # 500MB+
        if large_apps:
            recommendations.append(f"Found {len(large_apps)} apps over 500MB - review if still needed")
        
        return recommendations

class SecurityAnalysisModule(DiagnosticModule):
    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        """Analyze device security status"""
        try:
            # Check passcode status
            passcode_result = subprocess.run([
                'ideviceinfo', '-u', device.udid, '-k', 'PasswordProtected'
            ], capture_output=True, text=True)
            
            # Check activation lock
            activation_result = subprocess.run([
                'ideviceinfo', '-u', device.udid, '-k', 'ActivationState'
            ], capture_output=True, text=True)
            
            # Check if device is supervised
            supervised_result = subprocess.run([
                'ideviceinfo', '-u', device.udid, '-k', 'IsSupervised'
            ], capture_output=True, text=True)
            
            passcode_enabled = passcode_result.stdout.strip().lower() == 'true' if passcode_result.returncode == 0 else None
            activation_state = activation_result.stdout.strip() if activation_result.returncode == 0 else None
            is_supervised = supervised_result.stdout.strip().lower() == 'true' if supervised_result.returncode == 0 else None
            
            security_score = self._calculate_security_score(passcode_enabled, activation_state, is_supervised)
            
            return {
                "passcode_enabled": passcode_enabled,
                "activation_state": activation_state,
                "is_supervised": is_supervised,
                "security_score": security_score,
                "security_level": self._get_security_level(security_score),
                "recommendations": self._get_security_recommendations(passcode_enabled, activation_state, is_supervised)
            }
        except Exception as e:
            return {"error": f"Security analysis failed: {str(e)}"}
    
    def _calculate_security_score(self, passcode: bool, activation: str, supervised: bool) -> int:
        score = 0
        if passcode:
            score += 40
        if activation == "Activated":
            score += 30
        if supervised:
            score += 30
        return score
    
    def _get_security_level(self, score: int) -> str:
        if score >= 80:
            return "High"
        elif score >= 50:
            return "Medium"
        else:
            return "Low"
    
    def _get_security_recommendations(self, passcode: bool, activation: str, supervised: bool) -> List[str]:
        recommendations = []
        
        if not passcode:
            recommendations.append("Enable device passcode for security")
        
        if activation != "Activated":
            recommendations.append("Ensure device is properly activated")
        
        recommendations.extend([
            "Enable two-factor authentication for Apple ID",
            "Keep iOS updated to latest version",
            "Review app permissions regularly"
        ])
        
        return recommendations

class PerformanceProfiler(DiagnosticModule):
    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        """Profile device performance metrics"""
        try:
            # Get device model info for performance baseline
            model_result = subprocess.run([
                'ideviceinfo', '-u', device.udid, '-k', 'HardwareModel'
            ], capture_output=True, text=True)
            
            # Get CPU info
            cpu_result = subprocess.run([
                'ideviceinfo', '-u', device.udid, '-k', 'CPUArchitecture'
            ], capture_output=True, text=True)
            
            # Get memory info
            memory_result = subprocess.run([
                'ideviceinfo', '-u', device.udid, '-k', 'TotalSystemAvailable'
            ], capture_output=True, text=True)
            
            hardware_model = model_result.stdout.strip() if model_result.returncode == 0 else "Unknown"
            cpu_arch = cpu_result.stdout.strip() if cpu_result.returncode == 0 else "Unknown"
            total_memory = int(memory_result.stdout.strip()) if memory_result.returncode == 0 else 0
            
            performance_rating = self._assess_performance(hardware_model, cpu_arch, total_memory)
            
            return {
                "hardware_model": hardware_model,
                "cpu_architecture": cpu_arch,
                "total_memory_gb": round(total_memory / (1024**3), 2) if total_memory else 0,
                "performance_rating": performance_rating,
                "bottlenecks": self._identify_bottlenecks(total_memory),
                "recommendations": self._get_performance_recommendations(performance_rating, total_memory)
            }
        except Exception as e:
            return {"error": f"Performance profiling failed: {str(e)}"}
    
    def _assess_performance(self, model: str, cpu: str, memory: int) -> str:
        # Simplified performance assessment based on specs
        if "iPhone1" in model or memory < 2*1024**3:  # < 2GB RAM
            return "Low"
        elif "iPhone" in model and any(x in model for x in ["12", "13", "14", "15"]):
            return "High"
        else:
            return "Medium"
    
    def _identify_bottlenecks(self, memory: int) -> List[str]:
        bottlenecks = []
        
        if memory < 2*1024**3:  # < 2GB
            bottlenecks.append("Low RAM may cause app crashes")
        
        if memory < 4*1024**3:  # < 4GB
            bottlenecks.append("Limited multitasking capability")
        
        return bottlenecks
    
    def _get_performance_recommendations(self, rating: str, memory: int) -> List[str]:
        recommendations = []
        
        if rating == "Low":
            recommendations.extend([
                "Close background apps regularly",
                "Reduce visual effects",
                "Disable background app refresh for unused apps"
            ])
        
        if memory < 3*1024**3:  # < 3GB
            recommendations.append("Limit number of open apps")
        
        recommendations.extend([
            "Restart device weekly",
            "Keep iOS updated",
            "Monitor app usage in Settings"
        ])
        
        return recommendations

class ThermalMonitor(DiagnosticModule):
    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        """Monitor device thermal status"""
        try:
            # Get thermal state (iOS 11+)
            thermal_result = subprocess.run([
                'ideviceinfo', '-u', device.udid, '-k', 'ThermalState'
            ], capture_output=True, text=True)
            
            thermal_state = thermal_result.stdout.strip() if thermal_result.returncode == 0 else "Unknown"
            
            # Simulate temperature reading (real implementation would use more sophisticated methods)
            temp_celsius = self._estimate_temperature(thermal_state)
            
            return {
                "thermal_state": thermal_state,
                "estimated_temp_celsius": temp_celsius,
                "temp_status": self._get_temp_status(temp_celsius),
                "recommendations": self._get_thermal_recommendations(thermal_state, temp_celsius)
            }
        except Exception as e:
            return {"error": f"Thermal monitoring failed: {str(e)}"}
    
    def _estimate_temperature(self, thermal_state: str) -> int:
        """Estimate temperature based on thermal state"""
        temp_map = {
            "Normal": 35,
            "Fair": 42,
            "Serious": 48,
            "Critical": 55,
            "Unknown": 40
        }
        return temp_map.get(thermal_state, 40)
    
    def _get_temp_status(self, temp: int) -> str:
        if temp < 40:
            return "Normal"
        elif temp < 45:
            return "Warm"
        elif temp < 50:
            return "Hot"
        else:
            return "Overheating"
    
    def _get_thermal_recommendations(self, thermal_state: str, temp: int) -> List[str]:
        recommendations = []
        
        if thermal_state in ["Serious", "Critical"] or temp > 45:
            recommendations.extend([
                "Remove device from direct sunlight",
                "Close demanding applications",
                "Remove device case temporarily",
                "Allow device to cool down"
            ])
        
        if temp > 50:
            recommendations.append("Turn off device until it cools down")
        
        recommendations.extend([
            "Avoid charging while using intensive apps",
            "Use official Apple chargers only"
        ])
        
        return recommendations

class BackupManager(DiagnosticModule):
    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        """Advanced backup management and analysis"""
        try:
            # Check backup status
            backup_result = subprocess.run([
                'ideviceinfo', '-u', device.udid, '-k', 'LastBackupDate'
            ], capture_output=True, text=True)
            
            # Get backup encryption status
            encryption_result = subprocess.run([
                'ideviceinfo', '-u', device.udid, '-k', 'WillEncrypt'
            ], capture_output=True, text=True)
            
            last_backup = backup_result.stdout.strip() if backup_result.returncode == 0 else None
            backup_encrypted = encryption_result.stdout.strip().lower() == 'true' if encryption_result.returncode == 0 else None
            
            backup_status = self._assess_backup_status(last_backup)
            
            return {
                "last_backup_date": last_backup,
                "backup_encrypted": backup_encrypted,
                "backup_status": backup_status,
                "backup_locations": self._find_backup_locations(device.udid),
                "recommendations": self._get_backup_recommendations(backup_status, backup_encrypted)
            }
        except Exception as e:
            return {"error": f"Backup analysis failed: {str(e)}"}
    
    def _assess_backup_status(self, last_backup: str) -> str:
        if not last_backup or last_backup == "(null)":
            return "Never"
        
        try:
            from datetime import datetime, timedelta
            # Parse backup date (simplified)
            # Real implementation would parse the actual date format
            return "Recent"  # Placeholder
        except:
            return "Unknown"
    
    def _find_backup_locations(self, udid: str) -> List[str]:
        """Find local backup locations"""
        locations = []
        
        # Common macOS backup locations
        backup_paths = [
            Path.home() / "Library/Application Support/MobileSync/Backup",
            Path("/Library/Application Support/MobileSync/Backup")
        ]
        
        for path in backup_paths:
            if path.exists():
                for backup_dir in path.iterdir():
                    if backup_dir.is_dir() and udid.lower() in backup_dir.name.lower():
                        locations.append(str(backup_dir))
        
        return locations
    
    def _get_backup_recommendations(self, status: str, encrypted: bool) -> List[str]:
        recommendations = []
        
        if status == "Never":
            recommendations.extend([
                "Create regular backups",
                "Enable iCloud backup or iTunes backup"
            ])
        
        if not encrypted:
            recommendations.append("Enable encrypted backups for complete data protection")
        
        recommendations.extend([
            "Verify backup integrity regularly",
            "Store backups in multiple locations",
            "Test backup restoration process"
        ])
        
        return recommendations

class AccessibilityAnalyzer(DiagnosticModule):
    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        """Analyze accessibility settings and features"""
        try:
            # Check VoiceOver status
            voiceover_result = subprocess.run([
                'ideviceinfo', '-u', device.udid, '-k', 'VoiceOverTouchEnabled'
            ], capture_output=True, text=True)
            
            # Check Zoom status
            zoom_result = subprocess.run([
                'ideviceinfo', '-u', device.udid, '-k', 'ZoomTouchEnabled'
            ], capture_output=True, text=True)
            
            voiceover_enabled = voiceover_result.stdout.strip().lower() == 'true' if voiceover_result.returncode == 0 else False
            zoom_enabled = zoom_result.stdout.strip().lower() == 'true' if zoom_result.returncode == 0 else False
            
            accessibility_score = self._calculate_accessibility_score(voiceover_enabled, zoom_enabled)
            
            return {
                "voiceover_enabled": voiceover_enabled,
                "zoom_enabled": zoom_enabled,
                "accessibility_score": accessibility_score,
                "available_features": self._get_available_accessibility_features(),
                "recommendations": self._get_accessibility_recommendations(voiceover_enabled, zoom_enabled)
            }
        except Exception as e:
            return {"error": f"Accessibility analysis failed: {str(e)}"}
    
    def _calculate_accessibility_score(self, voiceover: bool, zoom: bool) -> int:
        """Calculate accessibility configuration score"""
        score = 50  # Base score
        if voiceover:
            score += 25
        if zoom:
            score += 25
        return score
    
    def _get_available_accessibility_features(self) -> List[str]:
        """List available accessibility features"""
        return [
            "VoiceOver",
            "Zoom",
            "Magnifier",
            "Display Accommodations",
            "Motion",
            "Spoken Content",
            "Audio Descriptions"
        ]
    
    def _get_accessibility_recommendations(self, voiceover: bool, zoom: bool) -> List[str]:
        recommendations = [
            "Review accessibility settings in Settings > Accessibility",
            "Enable shortcuts for frequently used features",
            "Test app compatibility with accessibility features"
        ]
        
        if not voiceover and not zoom:
            recommendations.append("Consider enabling accessibility features if needed")
        
        return recommendations

class CrashLogAnalyzer(DiagnosticModule):
    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        """Analyze crash logs for issues"""
        try:
            # Get crash logs directory
            logs_dir = Path.home() / "Library/Logs/CrashReporter/MobileDevice" / device.name
            
            if not logs_dir.exists():
                return {"error": "No crash logs found"}
            
            crash_files = list(logs_dir.glob("*.crash"))[-10:]  # Last 10 crashes
            
            crashes = []
            for crash_file in crash_files:
                with open(crash_file, 'r') as f:
                    content = f.read()
                    
                crashes.append({
                    "file": crash_file.name,
                    "timestamp": crash_file.stat().st_mtime,
                    "app": self._extract_app_name(content),
                    "reason": self._extract_crash_reason(content)
                })
            
            return {
                "total_crashes": len(crashes),
                "recent_crashes": crashes,
                "recommendations": self._get_crash_recommendations(crashes)
            }
        except Exception as e:
            return {"error": f"Crash log analysis failed: {str(e)}"}
    
    def _extract_app_name(self, content: str) -> str:
        for line in content.split('\n')[:10]:
            if 'Process:' in line:
                return line.split('Process:')[1].strip().split()[0]
        return "Unknown"
    
    def _extract_crash_reason(self, content: str) -> str:
        for line in content.split('\n'):
            if 'Exception Type:' in line:
                return line.split('Exception Type:')[1].strip()
        return "Unknown"
    
    def _get_crash_recommendations(self, crashes: List[Dict]) -> List[str]:
        recommendations = []
        
        if len(crashes) > 5:
            recommendations.append("Multiple crashes detected - consider device restart")
        
        app_crashes = {}
        for crash in crashes:
            app = crash['app']
            app_crashes[app] = app_crashes.get(app, 0) + 1
        
        for app, count in app_crashes.items():
            if count > 2:
                recommendations.append(f"App '{app}' crashing frequently - consider update/reinstall")
        
        return recommendations

class iSpyTool:
    def __init__(self):
        self.ai_engine = AIEngine()
        self.module_manager = ModuleManager()
        self.setup_modules()
        self.setup_logging()
    
    def setup_modules(self):
        """Register all diagnostic modules"""
        self.module_manager.register_module("battery", BatteryDiagnostic)
        self.module_manager.register_module("storage", StorageDiagnostic)
        self.module_manager.register_module("network", NetworkDiagnostic)
        self.module_manager.register_module("crashes", CrashLogAnalyzer)
        self.module_manager.register_module("apps", AppManagementModule)
        self.module_manager.register_module("security", SecurityAnalysisModule)
        self.module_manager.register_module("performance", PerformanceProfiler)
        self.module_manager.register_module("thermal", ThermalMonitor)
        self.module_manager.register_module("backup", BackupManager)
        self.module_manager.register_module("accessibility", AccessibilityAnalyzer)
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path.home() / ".ispy"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "ispy.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_connected_devices(self) -> List[DeviceInfo]:
        """Get list of connected iOS devices"""
        try:
            result = subprocess.run(['idevice_id', '-l'], capture_output=True, text=True)
            
            if result.returncode != 0:
                console.print("[red]No iOS devices found or libimobiledevice not installed[/red]")
                return []
            
            udids = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            devices = []
            
            for udid in udids:
                device_info = self.get_device_info(udid)
                if device_info:
                    devices.append(device_info)
            
            return devices
        except Exception as e:
            self.logger.error(f"Failed to get connected devices: {e}")
            return []
    
    def get_device_info(self, udid: str) -> Optional[DeviceInfo]:
        """Get detailed information about a device"""
        try:
            info_result = subprocess.run(['ideviceinfo', '-u', udid], capture_output=True, text=True)
            
            if info_result.returncode != 0:
                return None
            
            info_lines = info_result.stdout.split('\n')
            info_dict = {}
            
            for line in info_lines:
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    info_dict[key] = value
            
            return DeviceInfo(
                name=info_dict.get('DeviceName', 'Unknown'),
                model=info_dict.get('ProductType', 'Unknown'),
                version=info_dict.get('ProductVersion', 'Unknown'),
                udid=udid,
                serial=info_dict.get('SerialNumber', 'Unknown')
            )
        except Exception as e:
            self.logger.error(f"Failed to get device info for {udid}: {e}")
            return None
    
    def run_comprehensive_diagnostic(self, device: DeviceInfo) -> Dict[str, Any]:
        """Run all diagnostic modules on a device"""
        results = {}
        modules = self.module_manager.get_available_modules()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("Running diagnostics...", total=len(modules))
            
            for module_name in modules:
                progress.update(task, description=f"Running {module_name} diagnostic...")
                results[module_name] = self.module_manager.run_module(module_name, device)
                progress.advance(task)
        
        return results
    
    def generate_report(self, device: DeviceInfo, diagnostics: Dict[str, Any]) -> str:
        """Generate comprehensive diagnostic report"""
        report = f"""
# iSpy Diagnostic Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Device Information
- Name: {device.name}
- Model: {device.model}
- iOS Version: {device.version}
- Serial: {device.serial}
- UDID: {device.udid}

## Diagnostic Results
"""
        
        for module_name, results in diagnostics.items():
            report += f"\n### {module_name.title()} Analysis\n"
            
            if "error" in results:
                report += f"❌ Error: {results['error']}\n"
                continue
            
            # Format results based on module type
            if module_name == "battery":
                report += f"- Battery Level: {results.get('battery_level', 'Unknown')}%\n"
                report += f"- Cycle Count: {results.get('cycle_count', 'Unknown')}\n"
                report += f"- Health Status: {results.get('health_status', 'Unknown')}\n"
            
            elif module_name == "storage":
                report += f"- Total Storage: {results.get('total_storage_gb', 'Unknown')} GB\n"
                report += f"- Used Storage: {results.get('used_storage_gb', 'Unknown')} GB\n"
                report += f"- Free Storage: {results.get('free_storage_gb', 'Unknown')} GB\n"
                report += f"- Usage: {results.get('usage_percent', 'Unknown')}%\n"
                report += f"- Status: {results.get('status', 'Unknown')}\n"
            
            elif module_name == "network":
                report += f"- WiFi Connected: {results.get('wifi_connected', 'Unknown')}\n"
                report += f"- Cellular Available: {results.get('has_cellular', 'Unknown')}\n"
                report += f"- Status: {results.get('connectivity_status', 'Unknown')}\n"
            
            elif module_name == "crashes":
                report += f"- Total Crashes: {results.get('total_crashes', 'Unknown')}\n"
            
            # Add recommendations
            if "recommendations" in results:
                report += "\n**Recommendations:**\n"
                for rec in results["recommendations"]:
                    report += f"- {rec}\n"
        
        return report
    
    def interactive_mode(self):
        """Run interactive diagnostic mode"""
        console.print(Panel.fit(
            "[bold blue]iSpy - Advanced iOS Diagnostic Tool[/bold blue]\n"
            "AI-powered device analysis and troubleshooting",
            border_style="blue"
        ))
        
        devices = self.get_connected_devices()
        
        if not devices:
            console.print("[red]No iOS devices connected. Please connect a device and try again.[/red]")
            return
        
        # Display connected devices
        table = Table(title="Connected Devices")
        table.add_column("Name", style="cyan")
        table.add_column("Model", style="magenta")
        table.add_column("iOS Version", style="green")
        table.add_column("UDID", style="yellow")
        
        for i, device in enumerate(devices):
            table.add_row(device.name, device.model, device.version, device.udid[:8] + "...")
        
        console.print(table)
        
        # Select device
        if len(devices) == 1:
            selected_device = devices[0]
        else:
            while True:
                try:
                    choice = int(input(f"\nSelect device (1-{len(devices)}): ")) - 1
                    if 0 <= choice < len(devices):
                        selected_device = devices[choice]
                        break
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Please enter a number")
        
        console.print(f"\n[green]Selected device: {selected_device.name}[/green]")
        
        while True:
            console.print("\n[bold]Available Actions:[/bold]")
            console.print("1. Run comprehensive diagnostic")
            console.print("2. Run specific module")
            console.print("3. AI troubleshooting assistant")
            console.print("4. Generate report")
            if ANALYTICS_AVAILABLE:
                console.print("5. Advanced analytics")
                console.print("6. Exit")
            else:
                console.print("5. Exit")
            
            choice = input("\nSelect action: ").strip()
            
            if choice == "1":
                diagnostics = self.run_comprehensive_diagnostic(selected_device)
                self.display_diagnostic_results(diagnostics)
            
            elif choice == "2":
                self.run_specific_module(selected_device)
            
            elif choice == "3":
                self.ai_troubleshooting_assistant(selected_device)
            
            elif choice == "4":
                diagnostics = self.run_comprehensive_diagnostic(selected_device)
                report = self.generate_report(selected_device, diagnostics)
                
                # Add analytics if available
                if ANALYTICS_AVAILABLE:
                    analytics = DeviceAnalytics(selected_device.udid)
                    analytics_report = analytics.generate_analytics_report()
                    report += "\n\n" + analytics_report
                
                report_file = Path.home() / f"ispy_report_{selected_device.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                with open(report_file, 'w') as f:
                    f.write(report)
                
                console.print(f"[green]Report saved to: {report_file}[/green]")
            
            elif choice == "5" and ANALYTICS_AVAILABLE:
                self.advanced_analytics_menu(selected_device)
            
            elif choice == "5" and not ANALYTICS_AVAILABLE:
                break
            
            elif choice == "6" and ANALYTICS_AVAILABLE:
                break
            
            else:
                console.print("[red]Invalid choice[/red]")
    
    def display_diagnostic_results(self, diagnostics: Dict[str, Any]):
        """Display diagnostic results in a formatted table"""
        for module_name, results in diagnostics.items():
            console.print(f"\n[bold]{module_name.title()} Results:[/bold]")
            
            if "error" in results:
                console.print(f"[red]Error: {results['error']}[/red]")
                continue
            
            # Create table for results
            table = Table()
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="yellow")
            table.add_column("Status", style="green")
            
            for key, value in results.items():
                if key == "recommendations":
                    continue
                
                status = "✅" if key.endswith("_status") and value == "Good" else ""
                table.add_row(key.replace("_", " ").title(), str(value), status)
            
            console.print(table)
            
            # Show recommendations
            if "recommendations" in results and results["recommendations"]:
                console.print("\n[bold]Recommendations:[/bold]")
                for rec in results["recommendations"]:
                    console.print(f"• {rec}")
    
    def run_specific_module(self, device: DeviceInfo):
        """Run a specific diagnostic module"""
        modules = self.module_manager.get_available_modules()
        
        console.print("\n[bold]Available Modules:[/bold]")
        for i, module in enumerate(modules, 1):
            console.print(f"{i}. {module}")
        
        try:
            choice = int(input(f"\nSelect module (1-{len(modules)}): ")) - 1
            if 0 <= choice < len(modules):
                module_name = modules[choice]
                console.print(f"\n[green]Running {module_name} diagnostic...[/green]")
                
                results = self.module_manager.run_module(module_name, device)
                self.display_diagnostic_results({module_name: results})
            else:
                console.print("[red]Invalid selection[/red]")
        except ValueError:
            console.print("[red]Please enter a number[/red]")
    
    def ai_troubleshooting_assistant(self, device: DeviceInfo):
        """Interactive AI troubleshooting assistant"""
        console.print("\n[bold blue]AI Troubleshooting Assistant[/bold blue]")
        console.print("Describe the issue you're experiencing with your device:")
        
        problem = input("\nProblem description: ").strip()
        
        if not problem:
            console.print("[red]Please provide a problem description[/red]")
            return
        
        console.print("\n[yellow]Analyzing problem with AI...[/yellow]")
        
        suggestion = self.ai_engine.suggest_solution(problem, device)
        
        console.print("\n[bold green]AI Recommendations:[/bold green]")
        console.print(Panel(suggestion, border_style="green"))
    
    def advanced_analytics_menu(self, device: DeviceInfo):
        """Advanced analytics menu"""
        if not ANALYTICS_AVAILABLE:
            console.print("[red]Advanced analytics not available. Install required dependencies.[/red]")
            return
        
        analytics = DeviceAnalytics(device.udid)
        
        while True:
            console.print("\n[bold blue]Advanced Analytics[/bold blue]")
            console.print("1. Collect current data")
            console.print("2. Analyze trends (7 days)")
            console.print("3. Analyze trends (30 days)")
            console.print("4. Generate analytics report")
            console.print("5. Create trend charts")
            console.print("6. Back to main menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                console.print("[yellow]Collecting device data...[/yellow]")
                data = analytics.collect_historical_data()
                console.print("[green]Data collected successfully![/green]")
                
                # Display collected data
                for metric_type, values in data.items():
                    console.print(f"\n[bold]{metric_type.title()} Data:[/bold]")
                    for key, value in values.items():
                        if key != 'timestamp':
                            console.print(f"  {key}: {value}")
            
            elif choice == "2":
                console.print("[yellow]Analyzing 7-day trends...[/yellow]")
                trends = analytics.analyze_trends(7)
                self.display_analytics_results(trends)
            
            elif choice == "3":
                console.print("[yellow]Analyzing 30-day trends...[/yellow]")
                trends = analytics.analyze_trends(30)
                self.display_analytics_results(trends)
            
            elif choice == "4":
                console.print("[yellow]Generating analytics report...[/yellow]")
                report = analytics.generate_analytics_report(30)
                
                report_file = Path.home() / f"ispy_analytics_{device.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                with open(report_file, 'w') as f:
                    f.write(report)
                
                console.print(f"[green]Analytics report saved to: {report_file}[/green]")
            
            elif choice == "5":
                console.print("[yellow]Creating trend charts...[/yellow]")
                charts = analytics.create_trend_charts(30)
                
                if charts:
                    console.print(f"[green]Created {len(charts)} charts:[/green]")
                    for chart in charts:
                        console.print(f"  📊 {chart}")
                else:
                    console.print("[yellow]No charts created - insufficient data[/yellow]")
            
            elif choice == "6":
                break
            
            else:
                console.print("[red]Invalid choice[/red]")
    
    def display_analytics_results(self, results: Dict[str, Any]):
        """Display analytics results"""
        if not results:
            console.print("[yellow]No trend data available. Use device for a few days and try again.[/yellow]")
            return
        
        table = Table(title="Trend Analysis Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Current", style="yellow")
        table.add_column("Trend", style="green")
        table.add_column("Prediction", style="magenta")
        table.add_column("Confidence", style="blue")
        
        for metric_name, result in results.items():
            trend_emoji = {
                "improving": "📈",
                "stable": "➡️",
                "degrading": "📉"
            }.get(result.trend, "❓")
            
            table.add_row(
                result.metric_name,
                str(result.current_value),
                f"{trend_emoji} {result.trend}",
                str(result.prediction) if result.prediction else "N/A",
                f"{result.confidence*100:.0f}%"
            )
        
        console.print(table)
        
        # Show recommendations
        console.print("\n[bold]Recommendations:[/bold]")
        for metric_name, result in results.items():
            if result.recommendations:
                console.print(f"\n[bold]{result.metric_name}:[/bold]")
                for rec in result.recommendations:
                    console.print(f"  • {rec}")

def main():
    parser = argparse.ArgumentParser(description="iSpy - Advanced iOS Diagnostic Tool")
    parser.add_argument("--device", "-d", help="Target device UDID")
    parser.add_argument("--module", "-m", help="Run specific diagnostic module")
    parser.add_argument("--report", "-r", action="store_true", help="Generate diagnostic report")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run interactive mode")
    
    args = parser.parse_args()
    
    ispy = iSpyTool()
    
    if args.interactive or not any([args.device, args.module, args.report]):
        ispy.interactive_mode()
    else:
        # Command line mode
        devices = ispy.get_connected_devices()
        
        if not devices:
            console.print("[red]No iOS devices connected[/red]")
            return
        
        target_device = None
        if args.device:
            target_device = next((d for d in devices if d.udid.startswith(args.device)), None)
        else:
            target_device = devices[0]
        
        if not target_device:
            console.print("[red]Target device not found[/red]")
            return
        
        if args.module:
            results = ispy.module_manager.run_module(args.module, target_device)
            ispy.display_diagnostic_results({args.module: results})
        
        if args.report:
            diagnostics = ispy.run_comprehensive_diagnostic(target_device)
            report = ispy.generate_report(target_device, diagnostics)
            
            report_file = f"ispy_report_{target_device.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, 'w') as f:
                f.write(report)
            
            console.print(f"[green]Report saved to: {report_file}[/green]")

if __name__ == "__main__":
    main()