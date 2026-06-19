from app.detectors.types import Detection


class PolicyEngine:
    DIRECT_IDENTIFIER_TYPES = {
        "EMAIL",
        "PHONE",
        "STUDENT_ID",
        "IBAN",
        "CREDIT_CARD",
    }

    SECRET_TYPES = {
        "JWT_TOKEN",
        "API_KEY",
        "DATABASE_URL",
        "PASSWORD_ASSIGNMENT",
    }

    def decide_action(self, detection: Detection, policy_mode: str) -> tuple[str, str]:
        if policy_mode == "monitor":
            return "warn", "Monitor mode only flags the sensitive entity without transformation."

        if policy_mode == "strict":
            return "tokenize", "Strict mode tokenizes every detected sensitive entity."

        # Balanced mode:
        # Tokenize secrets, credentials, high-risk entities, and direct identifiers.
        if detection.entity_type in self.SECRET_TYPES:
            return "tokenize", "Balanced mode tokenizes secrets and credentials."

        if detection.entity_type in self.DIRECT_IDENTIFIER_TYPES:
            return "tokenize", "Balanced mode tokenizes direct identifiers."

        if detection.risk_level in {"critical", "high"}:
            return "tokenize", "Balanced mode tokenizes high-risk or critical sensitive entities."

        return "warn", "Balanced mode warns for lower-risk entities without transformation."