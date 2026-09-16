# Copyright (c) 2026 Martial Systems LLC
"""Experiment 1 has one live W. Distinct templates never exceed 2."""

from __future__ import annotations

from typing import Any

from signforge.graphs._common import binary_graph

N_TEMPLATES_MAX = 2


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    n_live = int(state.get("n_live_w") or 0)
    n_max = int(state.get("n_templates_max") or N_TEMPLATES_MAX)
    if n_live < 1:
        v.append("no_live_w")
    if n_live > n_max:
        v.append("too_many_w")
    if n_live > N_TEMPLATES_MAX:
        v.append("templates_over_two")
    if bool(state.get("unique_w_per_fly")):
        v.append("unique_w_per_fly")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="sign.engine_shared",
        evaluate=_evaluate,
        extra=["n_live_w", "n_templates_max", "unique_w_per_fly"],
    )
