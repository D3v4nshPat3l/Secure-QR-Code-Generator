"""Shared data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Sensitivity(str, Enum):
    PUBLIC = "public"
    PERSONAL = "personal"
    SECRET = "secret"
    FINANCIAL = "financial"


@dataclass(frozen=True)
class Payload:
    kind: str
    data: str
    sensitivity: Sensitivity = Sensitivity.PUBLIC
    warnings: tuple[str, ...] = field(default_factory=tuple)
    redacted_data: str | None = None

    def preview(self, reveal_secrets: bool = False) -> str:
        if reveal_secrets or self.redacted_data is None:
            return self.data
        return self.redacted_data
