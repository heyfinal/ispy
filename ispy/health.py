"""
iSpy Health Score - Overall Device Health Assessment
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum

from .constants import (
    HEALTH_BATTERY_WEIGHT,
    HEALTH_STORAGE_WEIGHT,
    HEALTH_PERFORMANCE_WEIGHT,
    HEALTH_SECURITY_WEIGHT,
    HEALTH_THERMAL_WEIGHT,
    HEALTH_BACKUP_WEIGHT,
    BATTERY_CYCLE_GOOD,
    BATTERY_CYCLE_DEGRADED,
    STORAGE_HEALTHY,
    STORAGE_MODERATE,
    TEMP_NORMAL,
    TEMP_WARM,
)


class HealthGrade(Enum):
    """Health grade classifications"""
    EXCELLENT = "A+"
    GREAT = "A"
    GOOD = "B"
    FAIR = "C"
    POOR = "D"
    CRITICAL = "F"


@dataclass
class ComponentHealth:
    """Health assessment for a single component"""
    name: str
    score: float  # 0-100
    weight: float
    status: str
    details: str
    recommendations: List[str]


@dataclass
class HealthScore:
    """Overall device health score calculation"""

    battery_score: float = 0.0
    storage_score: float = 0.0
    performance_score: float = 0.0
    security_score: float = 0.0
    thermal_score: float = 0.0
    backup_score: float = 0.0

    components: Dict[str, ComponentHealth] = None

    def __post_init__(self):
        if self.components is None:
            self.components = {}

    @property
    def overall_score(self) -> float:
        """Calculate weighted overall health score (0-100)"""
        return (
            self.battery_score * HEALTH_BATTERY_WEIGHT +
            self.storage_score * HEALTH_STORAGE_WEIGHT +
            self.performance_score * HEALTH_PERFORMANCE_WEIGHT +
            self.security_score * HEALTH_SECURITY_WEIGHT +
            self.thermal_score * HEALTH_THERMAL_WEIGHT +
            self.backup_score * HEALTH_BACKUP_WEIGHT
        )

    @property
    def grade(self) -> HealthGrade:
        """Get letter grade based on overall score"""
        score = self.overall_score
        if score >= 95:
            return HealthGrade.EXCELLENT
        elif score >= 85:
            return HealthGrade.GREAT
        elif score >= 70:
            return HealthGrade.GOOD
        elif score >= 55:
            return HealthGrade.FAIR
        elif score >= 40:
            return HealthGrade.POOR
        else:
            return HealthGrade.CRITICAL

    @property
    def grade_emoji(self) -> str:
        """Get emoji for grade"""
        emojis = {
            HealthGrade.EXCELLENT: "🌟",
            HealthGrade.GREAT: "✅",
            HealthGrade.GOOD: "👍",
            HealthGrade.FAIR: "⚠️",
            HealthGrade.POOR: "🔶",
            HealthGrade.CRITICAL: "🔴",
        }
        return emojis.get(self.grade, "❓")

    @classmethod
    def calculate_battery_score(
        cls,
        level: Optional[int],
        cycle_count: Optional[int]
    ) -> ComponentHealth:
        """Calculate battery health score"""
        score = 100.0
        recommendations = []
        details = []

        if level is not None:
            details.append(f"Current level: {level}%")
            if level < 20:
                score -= 10
                recommendations.append("Charge device soon")

        if cycle_count is not None:
            details.append(f"Cycle count: {cycle_count}")
            if cycle_count < BATTERY_CYCLE_GOOD:
                pass  # Good
            elif cycle_count < BATTERY_CYCLE_DEGRADED:
                score -= 20
                recommendations.append("Battery showing wear - monitor performance")
            else:
                score -= 40
                recommendations.append("Battery replacement recommended")

        status = "Good" if score >= 80 else "Fair" if score >= 60 else "Poor"

        return ComponentHealth(
            name="Battery",
            score=max(0, score),
            weight=HEALTH_BATTERY_WEIGHT,
            status=status,
            details="; ".join(details) if details else "No data",
            recommendations=recommendations
        )

    @classmethod
    def calculate_storage_score(
        cls,
        usage_percent: Optional[float]
    ) -> ComponentHealth:
        """Calculate storage health score"""
        score = 100.0
        recommendations = []

        if usage_percent is None:
            return ComponentHealth(
                name="Storage",
                score=50.0,
                weight=HEALTH_STORAGE_WEIGHT,
                status="Unknown",
                details="Could not determine storage usage",
                recommendations=["Check storage in Settings"]
            )

        details = f"Storage used: {usage_percent:.1f}%"

        if usage_percent < STORAGE_HEALTHY:
            status = "Healthy"
        elif usage_percent < STORAGE_MODERATE:
            score -= 25
            status = "Moderate"
            recommendations.append("Consider cleaning up unused files")
        else:
            score -= 50
            status = "Critical"
            recommendations.extend([
                "Delete unused apps",
                "Clear cache and temporary files",
                "Move photos/videos to iCloud or backup",
                "Offload unused apps"
            ])

        return ComponentHealth(
            name="Storage",
            score=max(0, score),
            weight=HEALTH_STORAGE_WEIGHT,
            status=status,
            details=details,
            recommendations=recommendations
        )

    @classmethod
    def calculate_security_score(
        cls,
        passcode_enabled: Optional[bool],
        activation_state: Optional[str],
        is_supervised: Optional[bool]
    ) -> ComponentHealth:
        """Calculate security health score"""
        score = 0.0
        recommendations = []
        details = []

        if passcode_enabled:
            score += 40
            details.append("Passcode: Enabled")
        else:
            details.append("Passcode: Disabled")
            recommendations.append("Enable device passcode")

        if activation_state == "Activated":
            score += 30
            details.append("Activation: Active")
        else:
            details.append(f"Activation: {activation_state or 'Unknown'}")

        if is_supervised:
            score += 30
            details.append("Supervised: Yes")
        else:
            details.append("Supervised: No")

        # General security recommendations
        recommendations.extend([
            "Enable two-factor authentication",
            "Keep iOS updated",
        ])

        status = "High" if score >= 80 else "Medium" if score >= 50 else "Low"

        return ComponentHealth(
            name="Security",
            score=score,
            weight=HEALTH_SECURITY_WEIGHT,
            status=status,
            details="; ".join(details),
            recommendations=recommendations
        )

    @classmethod
    def calculate_thermal_score(
        cls,
        thermal_state: Optional[str],
        temp_celsius: Optional[int]
    ) -> ComponentHealth:
        """Calculate thermal health score"""
        score = 100.0
        recommendations = []

        if temp_celsius is None:
            temp_celsius = 40  # Assume normal

        details = f"Temperature: ~{temp_celsius}°C ({thermal_state or 'Unknown'})"

        if temp_celsius < TEMP_NORMAL:
            status = "Normal"
        elif temp_celsius < TEMP_WARM:
            score -= 15
            status = "Warm"
            recommendations.append("Monitor device temperature")
        else:
            score -= 40
            status = "Hot"
            recommendations.extend([
                "Remove from direct sunlight",
                "Close demanding apps",
                "Remove case temporarily",
                "Allow to cool down"
            ])

        return ComponentHealth(
            name="Thermal",
            score=max(0, score),
            weight=HEALTH_THERMAL_WEIGHT,
            status=status,
            details=details,
            recommendations=recommendations
        )

    @classmethod
    def calculate_backup_score(
        cls,
        last_backup: Optional[str],
        encrypted: Optional[bool]
    ) -> ComponentHealth:
        """Calculate backup health score"""
        score = 50.0  # Base score
        recommendations = []
        details = []

        if last_backup and last_backup != "(null)":
            score += 30
            details.append(f"Last backup: {last_backup}")
        else:
            details.append("Last backup: Never")
            recommendations.append("Create a backup immediately")

        if encrypted:
            score += 20
            details.append("Encrypted: Yes")
        else:
            details.append("Encrypted: No")
            recommendations.append("Enable encrypted backups")

        recommendations.extend([
            "Enable automatic iCloud backup",
            "Verify backup integrity periodically"
        ])

        status = "Good" if score >= 80 else "Fair" if score >= 50 else "Poor"

        return ComponentHealth(
            name="Backup",
            score=score,
            weight=HEALTH_BACKUP_WEIGHT,
            status=status,
            details="; ".join(details),
            recommendations=recommendations
        )

    @classmethod
    def from_diagnostics(cls, diagnostics: Dict[str, Any]) -> "HealthScore":
        """Create HealthScore from diagnostic results"""
        health = cls()
        health.components = {}

        # Battery
        if "battery" in diagnostics and "error" not in diagnostics["battery"]:
            battery_data = diagnostics["battery"]
            component = cls.calculate_battery_score(
                battery_data.get("battery_level"),
                battery_data.get("cycle_count")
            )
            health.battery_score = component.score
            health.components["battery"] = component

        # Storage
        if "storage" in diagnostics and "error" not in diagnostics["storage"]:
            storage_data = diagnostics["storage"]
            component = cls.calculate_storage_score(
                storage_data.get("usage_percent")
            )
            health.storage_score = component.score
            health.components["storage"] = component

        # Security
        if "security" in diagnostics and "error" not in diagnostics["security"]:
            security_data = diagnostics["security"]
            component = cls.calculate_security_score(
                security_data.get("passcode_enabled"),
                security_data.get("activation_state"),
                security_data.get("is_supervised")
            )
            health.security_score = component.score
            health.components["security"] = component

        # Thermal
        if "thermal" in diagnostics and "error" not in diagnostics["thermal"]:
            thermal_data = diagnostics["thermal"]
            component = cls.calculate_thermal_score(
                thermal_data.get("thermal_state"),
                thermal_data.get("estimated_temp_celsius")
            )
            health.thermal_score = component.score
            health.components["thermal"] = component

        # Backup
        if "backup" in diagnostics and "error" not in diagnostics["backup"]:
            backup_data = diagnostics["backup"]
            component = cls.calculate_backup_score(
                backup_data.get("last_backup_date"),
                backup_data.get("backup_encrypted")
            )
            health.backup_score = component.score
            health.components["backup"] = component

        # Performance (default to 70 if no specific data)
        health.performance_score = 70.0

        return health

    def get_summary(self) -> Dict[str, Any]:
        """Get health summary"""
        return {
            "overall_score": round(self.overall_score, 1),
            "grade": self.grade.value,
            "grade_emoji": self.grade_emoji,
            "components": {
                name: {
                    "score": round(comp.score, 1),
                    "status": comp.status,
                    "details": comp.details,
                }
                for name, comp in self.components.items()
            }
        }

    def get_top_recommendations(self, limit: int = 5) -> List[str]:
        """Get top priority recommendations across all components"""
        all_recs = []
        for component in self.components.values():
            if component.score < 80:  # Only from underperforming components
                all_recs.extend(component.recommendations[:2])
        return list(dict.fromkeys(all_recs))[:limit]  # Remove duplicates, limit


class HealthCalculator:
    """Health score calculator utility"""

    def calculate(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate health score from diagnostic data"""
        score = HealthScore()
        score.components = {}

        # Battery
        if 'battery_level' in health_data or 'battery_cycles' in health_data:
            component = HealthScore.calculate_battery_score(
                health_data.get('battery_level'),
                health_data.get('battery_cycles')
            )
            score.battery_score = component.score
            score.components['battery'] = component

        # Storage
        if 'storage_usage' in health_data:
            component = HealthScore.calculate_storage_score(
                health_data.get('storage_usage')
            )
            score.storage_score = component.score
            score.components['storage'] = component

        # Security
        if 'security_score' in health_data:
            score.security_score = health_data['security_score']

        # Thermal
        if 'thermal_status' in health_data:
            status = health_data['thermal_status']
            if status == 'Normal':
                score.thermal_score = 100
            elif status == 'Warning':
                score.thermal_score = 70
            elif status == 'Critical':
                score.thermal_score = 30
            else:
                score.thermal_score = 80

        # Network connectivity bonus
        if health_data.get('network_connected'):
            score.performance_score = 80
        else:
            score.performance_score = 60

        # Default backup score
        score.backup_score = 70

        return {
            'overall_score': round(score.overall_score, 1),
            'overall_grade': score.grade.value,
            'grade_emoji': score.grade_emoji,
            'components': {
                name: {
                    'score': round(comp.score, 1),
                    'status': comp.status,
                }
                for name, comp in score.components.items()
            }
        }
