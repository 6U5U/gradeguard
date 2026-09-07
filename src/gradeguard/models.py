from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Status(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass(frozen=True)
class Finding:
    check: str
    status: Status
    message: str
    path: Path | None = None
    line: int | None = None


@dataclass
class Report:
    project: Path
    findings: list[Finding] = field(default_factory=list)
    tests_output: str = ""

    @property
    def counts(self) -> dict[Status, int]:
        return {status: sum(item.status == status for item in self.findings) for status in Status}

    @property
    def passed(self) -> bool:
        return not any(item.status == Status.FAIL for item in self.findings)

