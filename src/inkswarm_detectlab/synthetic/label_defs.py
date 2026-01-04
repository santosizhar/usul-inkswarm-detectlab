"""Human-readable label definitions for the synthetic generator.

These are used in reports + notebooks so readers understand what each label is
meant to represent. In the MVP, labels are *synthetic scenarios*, not ground
truth about real attackers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class LabelDefinition:
    key: str
    title: str
    intent: str
    how_generated: str


def get_label_definitions() -> List[LabelDefinition]:
    """Return label definitions in a stable order."""
    return [
        LabelDefinition(
            key="label_replicators",
            title="Replicators",
            intent="Automated or semi-automated high-volume login attempts (spray / scripted).",
            how_generated=(
                "Assigned in the synthetic generator based on a per-row 'is_attacker' flag and "
                "an attack-campaign intensity bucket; deterministic given the generator seed."
            ),
        ),
        LabelDefinition(
            key="label_the_mule",
            title="The Mule",
            intent="Credential-stuffing / account takeover style attempts with stronger success bias.",
            how_generated=(
                "Assigned in the synthetic generator from the same attacker campaign scaffold; "
                "deterministic given the generator seed."
            ),
        ),
        LabelDefinition(
            key="label_the_chameleon",
            title="The Chameleon",
            intent="Evasive attacker behavior designed to blend into normal traffic.",
            how_generated=(
                "Assigned from the attacker campaign scaffold with higher 'stealth' characteristics; "
                "deterministic given the generator seed."
            ),
        ),
    ]


def as_markdown_table() -> str:
    """A compact markdown table for reports."""
    rows = [
        "| label key | title | intent | how generated |",
        "|---|---|---|---|",
    ]
    for d in get_label_definitions():
        rows.append(f"| `{d.key}` | {d.title} | {d.intent} | {d.how_generated} |")
    return "\n".join(rows)
