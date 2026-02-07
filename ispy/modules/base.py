"""
iSpy Base Module - Foundation for Diagnostic Modules
"""

import subprocess
import shutil
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

from ..device import DeviceInfo


class DiagnosticModule(ABC):
    """Base class for all diagnostic modules"""

    name: str = "base"
    description: str = "Base diagnostic module"
    requires_device: bool = True

    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        """Execute the diagnostic module"""
        raise NotImplementedError

    def _run_idevice_command(
        self,
        command: str,
        udid: str,
        key: Optional[str] = None,
        domain: Optional[str] = None
    ) -> Optional[str]:
        """Run an idevice command and return output"""
        try:
            cmd = [command, '-u', udid]
            if domain:
                cmd.extend(['-q', domain])
            if key:
                cmd.extend(['-k', key])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None

    def _get_device_key(self, udid: str, key: str, domain: Optional[str] = None) -> Optional[str]:
        """Get a specific key from ideviceinfo"""
        return self._run_idevice_command('ideviceinfo', udid, key, domain=domain)

    def _check_tool_available(self, tool: str) -> bool:
        """Check if a command-line tool is available"""
        return shutil.which(tool) is not None

    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human-readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.2f} PB"


class ModuleManager:
    """Manages diagnostic modules"""

    def __init__(self):
        self.modules: Dict[str, type] = {}

    def register_module(self, name: str, module_class: type):
        """Register a diagnostic module"""
        self.modules[name] = module_class

    def register_all_modules(self):
        """Register all built-in modules"""
        from . import AVAILABLE_MODULES
        for name, module_class in AVAILABLE_MODULES.items():
            self.register_module(name, module_class)

    def get_available_modules(self) -> List[str]:
        """Get list of available module names"""
        return list(self.modules.keys())

    def get_module_info(self) -> Dict[str, str]:
        """Get module names and descriptions"""
        return {
            name: cls.description if hasattr(cls, 'description') else name
            for name, cls in self.modules.items()
        }

    def run_module(self, name: str, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        """Execute a specific module"""
        if name not in self.modules:
            return {"error": f"Module '{name}' not found"}

        try:
            module = self.modules[name]()
            return module.run(device, **kwargs)
        except Exception as e:
            return {"error": f"Module execution failed: {str(e)}"}

    def run_all_modules(
        self,
        device: DeviceInfo,
        modules: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
        **kwargs
    ) -> Dict[str, Dict[str, Any]]:
        """Run multiple modules"""
        modules_to_run = modules or self.get_available_modules()
        results = {}

        total = len(modules_to_run)
        for index, module_name in enumerate(modules_to_run, start=1):
            if module_name in self.modules:
                results[module_name] = self.run_module(module_name, device, **kwargs)
                if progress_callback:
                    progress_callback(module_name, index, total)

        return results
