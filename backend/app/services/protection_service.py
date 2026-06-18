from app.detectors.types import Detection
from app.policies.engine import PolicyEngine


class ProtectionService:
    def __init__(self) -> None:
        self.policy_engine = PolicyEngine()

    def protect(
        self,
        text: str,
        detections: list[Detection],
        policy_mode: str,
    ) -> tuple[str, list[dict]]:
        replacements: list[dict] = []
        counters: dict[str, int] = {}

        protected_text = text

        for detection in sorted(detections, key=lambda item: item.start_index, reverse=True):
            action, reason = self.policy_engine.decide_action(detection, policy_mode)

            counters[detection.entity_type] = counters.get(detection.entity_type, 0) + 1
            replacement_value = f"[{detection.entity_type}_{counters[detection.entity_type]}]"

            if action == "tokenize":
                protected_text = (
                    protected_text[: detection.start_index]
                    + replacement_value
                    + protected_text[detection.end_index :]
                )
            else:
                replacement_value = detection.value

            replacements.append(
                {
                    "detection": detection,
                    "action": action,
                    "replacement_value": replacement_value,
                    "reason": reason,
                }
            )

        replacements.reverse()
        return protected_text, replacements