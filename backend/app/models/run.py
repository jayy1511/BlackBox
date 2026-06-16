import uuid
from sqlalchemy import String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Run(Base, TimestampMixin):
    __tablename__ = "runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    status: Mapped[str] = mapped_column(String(32), nullable=False, default="created")
    policy_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="balanced")

    model_provider: Mapped[str] = mapped_column(String(64), nullable=False, default="gemini")
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)

    input_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)

    raw_input_stored: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    raw_input: Mapped[str | None] = mapped_column(Text, nullable=True)

    protected_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    risk_level: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
