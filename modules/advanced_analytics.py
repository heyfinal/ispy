#!/usr/bin/env python3
"""
Advanced Analytics Module for iSpy
Provides deep device insights and predictive analysis
"""

import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

@dataclass
class AnalyticsResult:
    metric_name: str
    current_value: float
    trend: str  # "improving", "stable", "degrading"
    prediction: Optional[float]
    confidence: float
    recommendations: List[str]

class DeviceAnalytics:
    def __init__(self, device_udid: str):
        self.device_udid = device_udid
        self.data_dir = Path.home() / ".ispy" / "analytics" / device_udid
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_historical_data(self) -> Dict[str, List[Dict]]:
        """Collect and store historical device metrics"""
        timestamp = datetime.now().isoformat()
        
        # Battery metrics
        battery_data = self._get_battery_metrics()
        battery_data['timestamp'] = timestamp
        
        # Storage metrics  
        storage_data = self._get_storage_metrics()
        storage_data['timestamp'] = timestamp
        
        # Performance metrics
        performance_data = self._get_performance_metrics()
        performance_data['timestamp'] = timestamp
        
        # Save to historical data
        self._append_to_history('battery', battery_data)
        self._append_to_history('storage', storage_data)
        self._append_to_history('performance', performance_data)
        
        return {
            'battery': battery_data,
            'storage': storage_data,
            'performance': performance_data
        }
    
    def _get_battery_metrics(self) -> Dict[str, Any]:
        """Get detailed battery metrics"""
        try:
            # Battery level
            level_result = subprocess.run([
                'ideviceinfo', '-u', self.device_udid, '-k', 'BatteryCurrentCapacity'
            ], capture_output=True, text=True)
            
            # Cycle count
            cycle_result = subprocess.run([
                'ideviceinfo', '-u', self.device_udid, '-k', 'BatteryCycleCount'
            ], capture_output=True, text=True)
            
            # Charging state
            charging_result = subprocess.run([
                'ideviceinfo', '-u', self.device_udid, '-k', 'BatteryIsCharging'
            ], capture_output=True, text=True)
            
            return {
                'level': int(level_result.stdout.strip()) if level_result.returncode == 0 else None,
                'cycle_count': int(cycle_result.stdout.strip()) if cycle_result.returncode == 0 else None,
                'is_charging': charging_result.stdout.strip().lower() == 'true' if charging_result.returncode == 0 else None
            }
        except Exception:
            return {'level': None, 'cycle_count': None, 'is_charging': None}
    
    def _get_storage_metrics(self) -> Dict[str, Any]:
        """Get detailed storage metrics"""
        try:
            # Total capacity
            total_result = subprocess.run([
                'ideviceinfo', '-u', self.device_udid, '-k', 'TotalDiskCapacity'
            ], capture_output=True, text=True)
            
            # Available space
            available_result = subprocess.run([
                'ideviceinfo', '-u', self.device_udid, '-k', 'AmountDataAvailable'
            ], capture_output=True, text=True)
            
            total_bytes = int(total_result.stdout.strip()) if total_result.returncode == 0 else None
            available_bytes = int(available_result.stdout.strip()) if available_result.returncode == 0 else None
            
            used_bytes = total_bytes - available_bytes if total_bytes and available_bytes else None
            usage_percent = (used_bytes / total_bytes * 100) if total_bytes and used_bytes else None
            
            return {
                'total_gb': round(total_bytes / (1024**3), 2) if total_bytes else None,
                'used_gb': round(used_bytes / (1024**3), 2) if used_bytes else None,
                'available_gb': round(available_bytes / (1024**3), 2) if available_bytes else None,
                'usage_percent': round(usage_percent, 2) if usage_percent else None
            }
        except Exception:
            return {'total_gb': None, 'used_gb': None, 'available_gb': None, 'usage_percent': None}
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance-related metrics"""
        try:
            # Free memory (approximation)
            memory_result = subprocess.run([
                'ideviceinfo', '-u', self.device_udid, '-k', 'TotalSystemAvailable'
            ], capture_output=True, text=True)
            
            # Thermal state
            thermal_result = subprocess.run([
                'ideviceinfo', '-u', self.device_udid, '-k', 'ThermalState'
            ], capture_output=True, text=True)
            
            return {
                'total_memory_gb': round(int(memory_result.stdout.strip()) / (1024**3), 2) if memory_result.returncode == 0 else None,
                'thermal_state': thermal_result.stdout.strip() if thermal_result.returncode == 0 else None
            }
        except Exception:
            return {'total_memory_gb': None, 'thermal_state': None}
    
    def _append_to_history(self, metric_type: str, data: Dict[str, Any]):
        """Append data to historical records"""
        history_file = self.data_dir / f"{metric_type}_history.json"
        
        # Load existing history
        history = []
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
            except:
                history = []
        
        # Append new data
        history.append(data)
        
        # Keep only last 1000 entries
        if len(history) > 1000:
            history = history[-1000:]
        
        # Save updated history
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def analyze_trends(self, days: int = 30) -> Dict[str, AnalyticsResult]:
        """Analyze trends over specified time period"""
        results = {}
        
        # Analyze battery trends
        battery_analysis = self._analyze_battery_trends(days)
        if battery_analysis:
            results.update(battery_analysis)
        
        # Analyze storage trends  
        storage_analysis = self._analyze_storage_trends(days)
        if storage_analysis:
            results.update(storage_analysis)
        
        # Analyze performance trends
        performance_analysis = self._analyze_performance_trends(days)
        if performance_analysis:
            results.update(performance_analysis)
        
        return results
    
    def _analyze_battery_trends(self, days: int) -> Dict[str, AnalyticsResult]:
        """Analyze battery-related trends"""
        history_file = self.data_dir / "battery_history.json"
        
        if not history_file.exists():
            return {}
        
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            # Filter to specified time period
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_history = [
                entry for entry in history
                if datetime.fromisoformat(entry['timestamp']) >= cutoff_date
            ]
            
            if len(recent_history) < 3:
                return {}
            
            # Analyze battery level trend
            levels = [entry['level'] for entry in recent_history if entry['level'] is not None]
            cycle_counts = [entry['cycle_count'] for entry in recent_history if entry['cycle_count'] is not None]
            
            results = {}
            
            if levels:
                level_trend = self._calculate_trend(levels)
                results['battery_level'] = AnalyticsResult(
                    metric_name="Battery Level",
                    current_value=levels[-1],
                    trend=level_trend,
                    prediction=self._predict_next_value(levels),
                    confidence=0.7,
                    recommendations=self._get_battery_recommendations(level_trend, levels[-1])
                )
            
            if cycle_counts and len(cycle_counts) > 1:
                cycle_trend = self._calculate_trend(cycle_counts)
                results['battery_cycles'] = AnalyticsResult(
                    metric_name="Battery Cycles",
                    current_value=cycle_counts[-1],
                    trend=cycle_trend,
                    prediction=self._predict_next_value(cycle_counts),
                    confidence=0.8,
                    recommendations=self._get_cycle_recommendations(cycle_counts[-1])
                )
            
            return results
            
        except Exception:
            return {}
    
    def _analyze_storage_trends(self, days: int) -> Dict[str, AnalyticsResult]:
        """Analyze storage-related trends"""
        history_file = self.data_dir / "storage_history.json"
        
        if not history_file.exists():
            return {}
        
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            # Filter to specified time period
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_history = [
                entry for entry in history
                if datetime.fromisoformat(entry['timestamp']) >= cutoff_date
            ]
            
            if len(recent_history) < 3:
                return {}
            
            # Analyze storage usage trend
            usage_percents = [entry['usage_percent'] for entry in recent_history if entry['usage_percent'] is not None]
            
            results = {}
            
            if usage_percents:
                usage_trend = self._calculate_trend(usage_percents)
                results['storage_usage'] = AnalyticsResult(
                    metric_name="Storage Usage",
                    current_value=usage_percents[-1],
                    trend=usage_trend,
                    prediction=self._predict_next_value(usage_percents),
                    confidence=0.9,
                    recommendations=self._get_storage_recommendations(usage_trend, usage_percents[-1])
                )
            
            return results
            
        except Exception:
            return {}
    
    def _analyze_performance_trends(self, days: int) -> Dict[str, AnalyticsResult]:
        """Analyze performance-related trends"""
        history_file = self.data_dir / "performance_history.json"
        
        if not history_file.exists():
            return {}
        
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            # Filter to specified time period
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_history = [
                entry for entry in history
                if datetime.fromisoformat(entry['timestamp']) >= cutoff_date
            ]
            
            if len(recent_history) < 3:
                return {}
            
            # Analyze thermal state frequency
            thermal_states = [entry['thermal_state'] for entry in recent_history if entry['thermal_state']]
            
            results = {}
            
            if thermal_states:
                # Count thermal events
                thermal_issues = sum(1 for state in thermal_states if state not in ['Normal', 'Fair'])
                thermal_score = max(0, 100 - (thermal_issues / len(thermal_states) * 100))
                
                results['thermal_performance'] = AnalyticsResult(
                    metric_name="Thermal Performance",
                    current_value=thermal_score,
                    trend="stable" if thermal_score > 80 else "degrading",
                    prediction=None,
                    confidence=0.6,
                    recommendations=self._get_thermal_recommendations(thermal_score)
                )
            
            return results
            
        except Exception:
            return {}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return "stable"
        
        # Use linear regression to determine trend
        x = np.arange(len(values))
        y = np.array(values)
        
        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.1:
            return "improving"
        elif slope < -0.1:
            return "degrading"
        else:
            return "stable"
    
    def _predict_next_value(self, values: List[float]) -> Optional[float]:
        """Predict next value using simple linear regression"""
        if len(values) < 3:
            return None
        
        try:
            x = np.arange(len(values))
            y = np.array(values)
            
            # Fit linear model
            coeffs = np.polyfit(x, y, 1)
            
            # Predict next value
            next_x = len(values)
            prediction = coeffs[0] * next_x + coeffs[1]
            
            return round(prediction, 2)
        except:
            return None
    
    def _get_battery_recommendations(self, trend: str, current_level: float) -> List[str]:
        """Get battery-specific recommendations"""
        recommendations = []
        
        if trend == "degrading":
            recommendations.extend([
                "Battery performance declining - monitor closely",
                "Consider enabling Low Power Mode more frequently",
                "Reduce screen brightness and background app refresh"
            ])
        
        if current_level < 20:
            recommendations.append("Charge device soon to avoid shutdown")
        
        return recommendations
    
    def _get_cycle_recommendations(self, cycle_count: int) -> List[str]:
        """Get cycle count specific recommendations"""
        recommendations = []
        
        if cycle_count > 500:
            recommendations.extend([
                "Battery cycle count is high - consider replacement",
                "Enable Optimized Battery Charging",
                "Avoid frequent full charge/discharge cycles"
            ])
        
        if cycle_count > 1000:
            recommendations.append("Battery replacement strongly recommended")
        
        return recommendations
    
    def _get_storage_recommendations(self, trend: str, current_usage: float) -> List[str]:
        """Get storage-specific recommendations"""
        recommendations = []
        
        if trend == "degrading" or current_usage > 85:
            recommendations.extend([
                "Storage usage increasing rapidly",
                "Delete unused apps and files",
                "Enable Optimize iPhone Storage for Photos",
                "Review and delete large attachments"
            ])
        
        if current_usage > 95:
            recommendations.append("Critical storage level - immediate cleanup needed")
        
        return recommendations
    
    def _get_thermal_recommendations(self, thermal_score: float) -> List[str]:
        """Get thermal performance recommendations"""
        recommendations = []
        
        if thermal_score < 70:
            recommendations.extend([
                "Device overheating frequently",
                "Avoid intensive tasks while charging",
                "Remove case during heavy usage",
                "Keep device out of direct sunlight"
            ])
        
        return recommendations
    
    def generate_analytics_report(self, days: int = 30) -> str:
        """Generate comprehensive analytics report"""
        # Collect fresh data
        self.collect_historical_data()
        
        # Analyze trends
        trends = self.analyze_trends(days)
        
        report = f"""
# Device Analytics Report
**Device UDID:** {self.device_udid}
**Analysis Period:** {days} days
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Trend Analysis Summary

"""
        
        if not trends:
            report += "❌ Insufficient data for trend analysis. Please use the device for a few days and run again.\n"
            return report
        
        for metric_name, result in trends.items():
            trend_emoji = {
                "improving": "📈",
                "stable": "➡️", 
                "degrading": "📉"
            }.get(result.trend, "❓")
            
            report += f"""
### {result.metric_name} {trend_emoji}
- **Current Value:** {result.current_value}
- **Trend:** {result.trend.title()}
- **Prediction:** {result.prediction if result.prediction else 'N/A'}
- **Confidence:** {result.confidence * 100:.0f}%

**Recommendations:**
"""
            for rec in result.recommendations:
                report += f"- {rec}\n"
        
        return report
    
    def create_trend_charts(self, days: int = 30) -> List[str]:
        """Create trend visualization charts"""
        chart_paths = []
        
        # Battery trend chart
        battery_chart = self._create_battery_chart(days)
        if battery_chart:
            chart_paths.append(battery_chart)
        
        # Storage trend chart
        storage_chart = self._create_storage_chart(days)
        if storage_chart:
            chart_paths.append(storage_chart)
        
        return chart_paths
    
    def _create_battery_chart(self, days: int) -> Optional[str]:
        """Create battery trend chart"""
        history_file = self.data_dir / "battery_history.json"
        
        if not history_file.exists():
            return None
        
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            # Filter and prepare data
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_history = [
                entry for entry in history
                if datetime.fromisoformat(entry['timestamp']) >= cutoff_date
                and entry['level'] is not None
            ]
            
            if len(recent_history) < 2:
                return None
            
            dates = [datetime.fromisoformat(entry['timestamp']) for entry in recent_history]
            levels = [entry['level'] for entry in recent_history]
            
            # Create chart
            plt.figure(figsize=(12, 6))
            plt.plot(dates, levels, marker='o', linestyle='-', linewidth=2, markersize=4)
            plt.title('Battery Level Trend', fontsize=16, fontweight='bold')
            plt.xlabel('Date')
            plt.ylabel('Battery Level (%)')
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save chart
            chart_path = self.data_dir / f"battery_trend_{days}d.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception:
            return None
    
    def _create_storage_chart(self, days: int) -> Optional[str]:
        """Create storage trend chart"""
        history_file = self.data_dir / "storage_history.json"
        
        if not history_file.exists():
            return None
        
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            # Filter and prepare data
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_history = [
                entry for entry in history
                if datetime.fromisoformat(entry['timestamp']) >= cutoff_date
                and entry['usage_percent'] is not None
            ]
            
            if len(recent_history) < 2:
                return None
            
            dates = [datetime.fromisoformat(entry['timestamp']) for entry in recent_history]
            usage = [entry['usage_percent'] for entry in recent_history]
            
            # Create chart
            plt.figure(figsize=(12, 6))
            plt.plot(dates, usage, marker='s', linestyle='-', linewidth=2, markersize=4, color='orange')
            plt.title('Storage Usage Trend', fontsize=16, fontweight='bold')
            plt.xlabel('Date')
            plt.ylabel('Storage Usage (%)')
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.axhline(y=85, color='red', linestyle='--', alpha=0.7, label='Critical Level')
            plt.legend()
            plt.tight_layout()
            
            # Save chart
            chart_path = self.data_dir / f"storage_trend_{days}d.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception:
            return None