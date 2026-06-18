from app.detectors.types import Detection


class PolicyEngine:
    def decide_action(self, detection: Detection, policy_mode: str) -> tuple[str, str]:
        if policy_mode == "monitor":
            return "warn", "Monitor mode only flags the sensitive entity without transformation."

        if policy_mode == "strict":
            return "tokenize", "Strict mode tokenizes every detected sensitive entity."

        # Balanced mode
        if detection.risk_level in {"critical", "high"}:
            return "tokenize", "Balanced mode tokenizes high-risk or critical sensitive entities."

        return "warn", "Balanced mode warns for medium-risk entities without transformation."