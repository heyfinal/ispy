"""Security Diagnostic Module"""

import subprocess
from typing import Dict, Any, List, Optional
from .base import DiagnosticModule
from ..device import DeviceInfo


class SecurityDiagnostic(DiagnosticModule):
    """Analyze device security configuration"""

    name = "security"
    description = "Security configuration analysis"

    def run(self, device: DeviceInfo, **kwargs) -> Dict[str, Any]:
        try:
            passcode_enabled = self._get_device_key(device.udid, 'PasswordProtected')
            activation_state = self._get_device_key(device.udid, 'ActivationState')

            is_passcode_set = passcode_enabled == 'true' if passcode_enabled else None
            is_activated = activation_state == 'Activated' if activation_state else None

            security_score = self._calculate_security_score(
                is_passcode_set,
                is_activated,
                device.ios_version
            )

            return {
                "passcode_enabled": is_passcode_set,
                "activation_state": activation_state,
                "ios_version": device.ios_version,
                "security_score": security_score,
                "recommendations": self._get_recommendations(is_passcode_set, device.ios_version)
            }
        except Exception as e:
            return {"error": f"Security diagnostic failed: {str(e)}"}

    def _calculate_security_score(
        self,
        passcode: Optional[bool],
        activated: Optional[bool],
        ios_version: Optional[str]
    ) -> int:
        score = 50  # Base score

        if passcode:
            score += 25
        if activated:
            score += 10
        if ios_version:
            try:
                major = int(ios_version.split('.')[0])
                if major >= 17:
                    score += 15
                elif major >= 15:
                    score += 10
                elif major >= 13:
                    score += 5
            except (ValueError, IndexError):
                pass

        return min(score, 100)

    def _get_recommendations(self, passcode: Optional[bool], ios_version: Optional[str]) -> List[str]:
        recs = []

        if passcode is False:
            recs.append("Enable passcode protection immediately")
            recs.append("Consider using Face ID or Touch ID")

        if ios_version:
            try:
                major = int(ios_version.split('.')[0])
                if major < 15:
                    recs.append("Update iOS to receive security patches")
                elif major < 17:
                    recs.append("Consider updating to latest iOS for enhanced security")
            except (ValueError, IndexError):
                pass

        if not recs:
            recs.append("Security configuration looks good")

        return recs
