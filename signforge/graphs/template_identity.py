# Copyright (c) 2026 Martial Systems LLC
"""Female FlyWire 139255; male MaleCNS 166691; slice is not a unique reconstruction."""

from __future__ import annotations

from typing import Any

from signforge.graphs._common import binary_graph

FLYWIRE_N = 139_255
MALECNS_N = 166_691
SLICE_N_MAX = 80


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if int(state.get("female_n") or 0) != FLYWIRE_N:
        v.append("female_count")
    if int(state.get("male_n") or 0) != MALECNS_N:
        v.append("male_count")
    slice_n = int(state.get("slice_n") or 0)
    if slice_n <= 0 or slice_n > SLICE_N_MAX:
        v.append("slice_size")
    if slice_n >= MALECNS_N or slice_n >= FLYWIRE_N:
        v.append("slice_not_reduced")
    if bool(state.get("unique_reconstruction")):
        v.append("unique_reconstruction")
    if not bool(state.get("hop_count_extract")):
        v.append("need_hop_extract")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="sign.template_identity",
        evaluate=_evaluate,
        extra=[
            "female_n",
            "male_n",
            "slice_n",
            "unique_reconstruction",
            "hop_count_extract",
        ],
    )
