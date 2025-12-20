from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional

DType = Literal["string","bool","int64","float64","timestamp_tz"]

@dataclass(frozen=True)
class ColumnSpec:
    name: str
    dtype: DType
    required: bool = True
    enum: Optional[list[str]] = None
    description: str = ""

@dataclass(frozen=True)
class EventSchema:
    name: str
    version: str
    columns: list[ColumnSpec]
    description: str = ""

    def required_columns(self) -> list[str]:
        return [c.name for c in self.columns if c.required]

    def column_names(self) -> list[str]:
        return [c.name for c in self.columns]

    def to_markdown(self) -> str:
        lines = [
            f"# Schema: `{self.name}` (v{self.version})",
            "",
            self.description,
            "",
            "| column | dtype | required | enum | description |",
            "|---|---|---:|---|---|",
        ]
        for c in self.columns:
            enum = ", ".join(c.enum) if c.enum else ""
            lines.append(f"| `{c.name}` | {c.dtype} | {str(c.required).lower()} | {enum} | {c.description} |")
        return "\n".join(lines) + "\n"
