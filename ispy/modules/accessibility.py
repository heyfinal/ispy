"""Accessibility Diagnostic Module"""

from typing import Dict, Any, List, Optional
from .base import DiagnosticModule
from ..device import DeviceInfo


class AccessibilityDiagnostic(DiagnosticModule):
    """Analyze accessibility settings"""

    name = "accessibility"
    description = "Accessibility features status"

    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        try:
            # Check various accessibility features
            voiceover = self._get_device_key(device.udid, 'VoiceOverEnabled')
            zoom = self._get_device_key(device.udid, 'ZoomEnabled')
            bold_text = self._get_device_key(device.udid, 'BoldTextEnabled')
            larger_text = self._get_device_key(device.udid, 'LargerTextEnabled')
            reduce_motion = self._get_device_key(device.udid, 'ReduceMotionEnabled')
            increase_contrast = self._get_device_key(device.udid, 'IncreaseContrastEnabled')
            assistive_touch = self._get_device_key(device.udid, 'AssistiveTouchEnabled')

            features_enabled = []
            if voiceover == 'true':
                features_enabled.append("VoiceOver")
            if zoom == 'true':
                features_enabled.append("Zoom")
            if bold_text == 'true':
                features_enabled.append("Bold Text")
            if larger_text == 'true':
                features_enabled.append("Larger Text")
            if reduce_motion == 'true':
                features_enabled.append("Reduce Motion")
            if increase_contrast == 'true':
                features_enabled.append("Increase Contrast")
            if assistive_touch == 'true':
                features_enabled.append("AssistiveTouch")

            return {
                "voiceover_enabled": voiceover == 'true' if voiceover else None,
                "zoom_enabled": zoom == 'true' if zoom else None,
                "bold_text_enabled": bold_text == 'true' if bold_text else None,
                "larger_text_enabled": larger_text == 'true' if larger_text else None,
                "reduce_motion_enabled": reduce_motion == 'true' if reduce_motion else None,
                "increase_contrast_enabled": increase_contrast == 'true' if increase_contrast else None,
                "assistive_touch_enabled": assistive_touch == 'true' if assistive_touch else None,
                "features_enabled": features_enabled,
                "total_features_enabled": len(features_enabled),
                "recommendations": self._get_recommendations(features_enabled, reduce_motion)
            }
        except Exception as e:
            return {"error": f"Accessibility diagnostic failed: {str(e)}"}

    def _get_recommendations(self, features: List[str], reduce_motion: Optional[str]) -> List[str]:
        recs = []

        if "VoiceOver" in features:
            recs.append("VoiceOver is active - ensure apps support accessibility labels")

        if "Reduce Motion" not in features and len(features) > 0:
            recs.append("Consider enabling Reduce Motion to improve performance")

        if not features:
            recs.append("No accessibility features detected")
            recs.append("Explore Settings > Accessibility for available options")

        if len(features) >= 3:
            recs.append("Multiple accessibility features enabled - monitor battery impact")

        return recs if recs else ["Accessibility configuration reviewed"]
