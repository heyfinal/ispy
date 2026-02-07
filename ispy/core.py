"""
iSpy Core - Main Diagnostic Tool Class
"""

import json
import subprocess
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from datetime import datetime

from .device import DeviceInfo, detect_devices
from .modules import ModuleManager, AVAILABLE_MODULES
from .health import HealthCalculator
from .ai_engine import AIEngine
from .config import Config


class iSpyTool:
    """Main iSpy diagnostic tool"""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.module_manager = ModuleManager()
        self.module_manager.register_all_modules()
        self.health_calculator = HealthCalculator()
        self.ai_engine = None

        # Initialize AI if configured
        if self.config.ai_enabled and (self.config.get('openai_api_key') or self.config.get('gemini_api_key')):
            self.ai_engine = AIEngine(
                openai_api_key=self.config.get('openai_api_key'),
                gemini_api_key=self.config.get('gemini_api_key'),
                openai_model=self.config.get('ai_model'),
                gemini_model=self.config.get('gemini_model'),
                openai_base_url=self.config.get('openai_base_url'),
            )

    def get_connected_devices(self) -> List[DeviceInfo]:
        """Get all connected iOS devices"""
        return detect_devices()

    def get_device(self, udid: Optional[str] = None) -> Optional[DeviceInfo]:
        """Get a specific device or the first available"""
        devices = self.get_connected_devices()

        if not devices:
            return None

        if udid:
            for device in devices:
                if device.udid == udid:
                    return device
            return None

        return devices[0]

    def run_diagnostic(
        self,
        device: DeviceInfo,
        modules: Optional[List[str]] = None,
        include_ai: bool = False,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, Any]:
        """Run diagnostics on a device"""
        start_time = datetime.now()

        # Run specified modules or all
        modules_to_run = modules or self.module_manager.get_available_modules()
        results = self.module_manager.run_all_modules(
            device,
            modules_to_run,
            progress_callback=progress_callback
        )

        # Calculate health score
        health_data = self._extract_health_data(results)
        health_score = self.health_calculator.calculate(health_data)

        # Build report
        report = {
            "device": device.to_dict(),
            "timestamp": start_time.isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "health_score": health_score,
            "modules": results,
            "summary": self._generate_summary(results, health_score)
        }

        # Add AI analysis if requested and available
        if include_ai and self.ai_engine:
            ai_analysis = self.ai_engine.analyze_diagnostics(results, device)
            report["ai_analysis"] = ai_analysis

        return report

    def run_quick_check(self, device: DeviceInfo) -> Dict[str, Any]:
        """Run essential diagnostics only"""
        essential_modules = ['battery', 'storage', 'network', 'security']
        return self.run_diagnostic(device, modules=essential_modules)

    def run_full_diagnostic(self, device: DeviceInfo, include_ai: bool = True) -> Dict[str, Any]:
        """Run comprehensive diagnostics with AI analysis"""
        return self.run_diagnostic(device, include_ai=include_ai)

    def _extract_health_data(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract health-relevant data from module results"""
        health_data = {}

        # Battery
        if 'battery' in results and 'error' not in results['battery']:
            health_data['battery_level'] = results['battery'].get('battery_level')
            health_data['battery_cycles'] = results['battery'].get('cycle_count')

        # Storage
        if 'storage' in results and 'error' not in results['storage']:
            health_data['storage_usage'] = results['storage'].get('usage_percent')

        # Network
        if 'network' in results and 'error' not in results['network']:
            health_data['network_connected'] = (
                results['network'].get('wifi_connected') or
                results['network'].get('has_cellular')
            )

        # Security
        if 'security' in results and 'error' not in results['security']:
            health_data['security_score'] = results['security'].get('security_score')

        # Thermal
        if 'thermal' in results and 'error' not in results['thermal']:
            health_data['thermal_status'] = results['thermal'].get('status')

        return health_data

    def _generate_summary(self, results: Dict[str, Any], health_score: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of diagnostic results"""
        issues = []
        recommendations = []

        for module_name, module_results in results.items():
            if 'error' in module_results:
                issues.append(f"{module_name}: {module_results['error']}")
            elif 'recommendations' in module_results:
                for rec in module_results['recommendations']:
                    if rec and rec not in recommendations:
                        recommendations.append(rec)

        return {
            "overall_grade": health_score.get('overall_grade', 'N/A'),
            "overall_score": health_score.get('overall_score', 0),
            "issues_found": len(issues),
            "issues": issues,
            "top_recommendations": recommendations[:5],
            "modules_run": list(results.keys()),
            "modules_successful": len([r for r in results.values() if 'error' not in r])
        }

    def export_report(
        self,
        report: Dict[str, Any],
        output_path: Optional[Path] = None,
        format: str = 'json'
    ) -> Path:
        """Export diagnostic report to file"""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            device_name = report.get('device', {}).get('name', 'unknown')
            safe_name = "".join(c for c in device_name if c.isalnum() or c in '._-')
            output_path = Path(f"ispy_report_{safe_name}_{timestamp}.{format}")

        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        elif format == 'txt':
            with open(output_path, 'w') as f:
                f.write(self._format_text_report(report))
        else:
            raise ValueError(f"Unsupported format: {format}")

        return output_path

    def _format_text_report(self, report: Dict[str, Any]) -> str:
        """Format report as human-readable text"""
        lines = []
        lines.append("=" * 60)
        lines.append("iSpy iOS Diagnostic Report")
        lines.append("=" * 60)
        lines.append("")

        # Device info
        device = report.get('device', {})
        lines.append(f"Device: {device.get('name', 'Unknown')}")
        lines.append(f"Model: {device.get('model', 'Unknown')}")
        lines.append(f"iOS Version: {device.get('ios_version', 'Unknown')}")
        lines.append(f"UDID: {device.get('udid', 'Unknown')}")
        lines.append("")

        # Health score
        summary = report.get('summary', {})
        lines.append(f"Overall Health: {summary.get('overall_grade', 'N/A')} ({summary.get('overall_score', 0)}%)")
        lines.append("")

        # Module results
        lines.append("-" * 40)
        lines.append("Diagnostic Results")
        lines.append("-" * 40)

        for module_name, results in report.get('modules', {}).items():
            lines.append(f"\n[{module_name.upper()}]")
            if 'error' in results:
                lines.append(f"  Error: {results['error']}")
            else:
                for key, value in results.items():
                    if key != 'recommendations':
                        lines.append(f"  {key}: {value}")

        # Recommendations
        lines.append("")
        lines.append("-" * 40)
        lines.append("Recommendations")
        lines.append("-" * 40)
        for rec in summary.get('top_recommendations', []):
            lines.append(f"  • {rec}")

        # AI Analysis
        if 'ai_analysis' in report:
            lines.append("")
            lines.append("-" * 40)
            lines.append("AI Analysis")
            lines.append("-" * 40)
            lines.append(report['ai_analysis'])

        lines.append("")
        lines.append("=" * 60)
        lines.append(f"Report generated: {report.get('timestamp', 'Unknown')}")
        lines.append("=" * 60)

        return "\n".join(lines)

    def get_available_modules(self) -> Dict[str, str]:
        """Get list of available diagnostic modules"""
        return self.module_manager.get_module_info()

    def analyze_with_ai(self, prompt: str, context: Optional[Dict] = None) -> Optional[str]:
        """Get AI analysis for a specific question"""
        if not self.ai_engine:
            return None
        return self.ai_engine.ask(prompt, context)
