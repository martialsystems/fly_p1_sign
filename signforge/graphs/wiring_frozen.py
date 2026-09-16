# Copyright (c) 2026 Martial Systems LLC
"""Default Icarus transform never changes wiring_sex."""

from __future__ import annotations

from typing import Any

from signforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if bool(state.get("wiring_changed")):
        v.append("wiring_changed")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="sign.wiring_frozen",
        evaluate=_evaluate,
        extra=["wiring_changed"],
    )
