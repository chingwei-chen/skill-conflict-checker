from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def emoji(self) -> str:
        return {"high": "🔴", "medium": "🟡", "low": "🟢"}[self.value]


@dataclass
class ConflictingPair:
    source_a: str
    source_b: str


@dataclass
class Conflict:
    severity: Severity
    category: str
    title: str
    description: str
    sources: ConflictingPair
    recommendation: str

    @classmethod
    def from_dict(cls, data: dict) -> "Conflict":
        return cls(
            severity=Severity(data.get("severity", "low")),
            category=data.get("category", "unknown"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            sources=ConflictingPair(
                source_a=data.get("source_a", ""),
                source_b=data.get("source_b", ""),
            ),
            recommendation=data.get("recommendation", ""),
        )
