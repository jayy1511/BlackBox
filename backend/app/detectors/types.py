from dataclasses import dataclass


@dataclass(frozen=True)
class Detection:
    entity_type: str
    value: str
    start_index: int
    end_index: int
    confidence: float
    risk_level: str