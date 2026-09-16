# Copyright (c) 2026 Martial Systems LLC
"""Unfreeze, female-brain Icarus, and n>2 refuse until experiment 1 passes."""

from __future__ import annotations

from typing import Any

from signforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    n = int(state.get("n") or 0)
    passed = bool(state.get("exp1_passed"))
    if n < 2:
        v.append("need_two_agents")
    if n > 2 and not passed:
        v.append("n_before_exp1")
    if bool(state.get("unfreeze")) and not passed:
        v.append("unfreeze_before_exp1")
    if bool(state.get("female_brain_icarus")) and not passed:
        v.append("swap_before_exp1")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="sign.assay_order",
        evaluate=_evaluate,
        extra=["n", "unfreeze", "female_brain_icarus", "exp1_passed"],
    )
