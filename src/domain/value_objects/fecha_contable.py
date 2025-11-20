from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FechaContable:
    value: date

    @staticmethod
    def from_ddmmyyyy(s: str) -> "FechaContable":
        # s = "17/10/2025"
        dt = datetime.strptime(s.strip(), "%d%m%Y").date()
        return FechaContable(value=dt)

    def to_ddmmyyyy(self) -> str:
        return self.value.strftime("%d%m%Y")

    def to_yymmdd(self) -> str:
        return self.value.strftime("%y%m%d")