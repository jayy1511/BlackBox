import re

from app.detectors.types import Detection


class CustomSensitiveDataDetector:
    def __init__(self) -> None:
        self.patterns: list[tuple[str, str, str, float, re.Pattern[str]]] = [
            (
                "EMAIL",
                "medium",
                "Email address",
                0.98,
                re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
            ),
            (
                "PHONE",
                "medium",
                "Phone number",
                0.85,
                re.compile(r"(\+?\d[\d\s().-]{7,}\d)"),
            ),
            (
                "JWT_TOKEN",
                "critical",
                "JWT token",
                0.98,
                re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
            ),
            (
                "API_KEY",
                "critical",
                "API key",
                0.95,
                re.compile(r"\b(?:sk|pk|api|key|token)[-_]?(?:live|test|prod)?[-_]?[A-Za-z0-9]{16,}\b", re.IGNORECASE),
            ),
            (
                "DATABASE_URL",
                "critical",
                "Database URL",
                0.98,
                re.compile(r"\b(?:postgres|postgresql|mysql|mongodb|redis)://[^\s]+", re.IGNORECASE),
            ),
            (
                "PASSWORD_ASSIGNMENT",
                "critical",
                "Password assignment",
                0.9,
                re.compile(r"\b(password|passwd|pwd)\s*[:=]\s*[^\s,;]+", re.IGNORECASE),
            ),
            (
                "IBAN",
                "high",
                "IBAN",
                0.9,
                re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b"),
            ),
            (
                "CREDIT_CARD",
                "critical",
                "Credit card number",
                0.85,
                re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
            ),
            (
                "STUDENT_ID",
                "high",
                "Student ID",
                0.85,
                re.compile(r"\b[A-Z]{2,10}[-_]?\d{4,10}\b"),
            ),
            (
                "HEALTH_DATA",
                "high",
                "Health-related data",
                0.75,
                re.compile(
                    r"\b(depression|cancer|diabetes|anxiety|diagnosis|medical certificate|therapy|treatment|patient)\b",
                    re.IGNORECASE,
                ),
            ),
        ]

    def detect(self, text: str) -> list[Detection]:
        detections: list[Detection] = []

        for entity_type, risk_level, _label, confidence, pattern in self.patterns:
            for match in pattern.finditer(text):
                value = match.group(0)

                detections.append(
                    Detection(
                        entity_type=entity_type,
                        value=value,
                        start_index=match.start(),
                        end_index=match.end(),
                        confidence=confidence,
                        risk_level=risk_level,
                    )
                )

        return self._deduplicate(detections)

    def _deduplicate(self, detections: list[Detection]) -> list[Detection]:
        # Keep longer / higher-confidence detections when spans overlap.
        sorted_detections = sorted(
            detections,
            key=lambda item: (
                item.start_index,
                -(item.end_index - item.start_index),
                -item.confidence,
            ),
        )

        result: list[Detection] = []

        for detection in sorted_detections:
            overlaps = any(
                not (
                    detection.end_index <= existing.start_index
                    or detection.start_index >= existing.end_index
                )
                for existing in result
            )

            if not overlaps:
                result.append(detection)

        return sorted(result, key=lambda item: item.start_index)