"""
Map detection/VLM severity (critical, major, minor) to API/DB anomaly severity (high, med, low).
Use when syncing detection results → Anomaly records.
"""

from schemas.enums import AnomalySeverity


def defect_severity_to_anomaly(severity: str | None) -> AnomalySeverity:
    """Map defect severity from VLM/detection (critical|major|minor) to AnomalySeverity (high|med|low)."""
    if not severity:
        return AnomalySeverity.med
    s = severity.strip().lower()
    if s in ("critical", "high"):
        return AnomalySeverity.high
    if s in ("minor", "low"):
        return AnomalySeverity.low
    return AnomalySeverity.med
