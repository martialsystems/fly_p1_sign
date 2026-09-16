# Copyright (c) 2026 Martial Systems LLC
"""Call sites for refuse laws."""

from __future__ import annotations

import re
from typing import Any

from signforge._bootstrap import ensure_paths

ensure_paths()

from graphforge.product_law import LawBlockedError, require_law

from signforge.graphs.assay_order import build_graph as build_order
from signforge.graphs.claim_bans import build_graph as build_claims
from signforge.graphs.engine_shared import N_TEMPLATES_MAX, build_graph as build_engine
from signforge.graphs.template_identity import (
    FLYWIRE_N,
    MALECNS_N,
    SLICE_N_MAX,
    build_graph as build_templates,
)
from signforge.graphs.wiring_frozen import build_graph as build_wiring

UNIQUE_RE = re.compile(r"unique reconstructed|1,?000 unique", re.I)
SPIKE_RE = re.compile(
    r"(default|population).{0,40}(full[- ]cns|139k|167k|166k).{0,20}spike|"
    r"live (whole-cns|139k|167k|166k) LIF",
    re.I,
)
GROWN_RE = re.compile(r"grew a (new )?connectome|grown connectome", re.I)
LARVA_RE = re.compile(r"\b(larva|larvae|oenocyte)s?\b.{0,40}\b(reconstr|map|connectome)", re.I)
ANIM_RE = re.compile(r"\b(animation|renderer)\b.{0,40}\b(science|result|finding)\b", re.I)
PARENT_F_RE = re.compile(r"F = 0\.524|IBD F = 0\.524", re.I)
POP_CIRCUIT_RE = re.compile(
    r"(1,?000[- ]fly|population).{0,40}(answers|shows|proves).{0,40}P1|"
    r"P1.{0,40}(from|via|by) the (population|1,?000)",
    re.I,
)


def require_claims(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "icarus_claims"))
    state = {
        "unique_brains": False,
        "population_spike_LIF": False,
        "grown_connectome": False,
        "larvae_oenocytes": False,
        "animation_as_science": False,
        "parent_f_restamp": False,
        "population_answers_circuit": False,
    }
    state.update(flags)
    require_law(
        build_claims(),
        state,
        allow_decisions=["allow"],
        law_id="sign.claim_bans",
        thread_id=thread_id,
        raise_error=True,
    )


def require_wiring(*, wiring_changed: bool = False) -> None:
    require_law(
        build_wiring(),
        {"wiring_changed": bool(wiring_changed)},
        allow_decisions=["allow"],
        law_id="sign.wiring_frozen",
        thread_id="wiring_frozen",
        raise_error=True,
    )


def require_engine(
    *,
    n_live_w: int = 1,
    n_templates_max: int = N_TEMPLATES_MAX,
    unique_w_per_fly: bool = False,
) -> None:
    require_law(
        build_engine(),
        {
            "n_live_w": int(n_live_w),
            "n_templates_max": int(n_templates_max),
            "unique_w_per_fly": bool(unique_w_per_fly),
        },
        allow_decisions=["allow"],
        law_id="sign.engine_shared",
        thread_id="engine_shared",
        raise_error=True,
    )


def require_templates(
    *,
    female_n: int = FLYWIRE_N,
    male_n: int = MALECNS_N,
    slice_n: int,
    unique_reconstruction: bool = False,
    hop_count_extract: bool = True,
) -> None:
    require_law(
        build_templates(),
        {
            "female_n": int(female_n),
            "male_n": int(male_n),
            "slice_n": int(slice_n),
            "unique_reconstruction": bool(unique_reconstruction),
            "hop_count_extract": bool(hop_count_extract),
        },
        allow_decisions=["allow"],
        law_id="sign.template_identity",
        thread_id="template_identity",
        raise_error=True,
    )


def require_assay_order(
    *,
    n: int,
    unfreeze: bool = False,
    female_brain_icarus: bool = False,
    exp1_passed: bool = False,
) -> None:
    require_law(
        build_order(),
        {
            "n": int(n),
            "unfreeze": bool(unfreeze),
            "female_brain_icarus": bool(female_brain_icarus),
            "exp1_passed": bool(exp1_passed),
        },
        allow_decisions=["allow"],
        law_id="sign.assay_order",
        thread_id="assay_order",
        raise_error=True,
    )


def scan_text_flags(text: str) -> dict[str, bool]:
    t = text or ""
    return {
        "unique_brains": bool(UNIQUE_RE.search(t)),
        "population_spike_LIF": bool(SPIKE_RE.search(t)),
        "grown_connectome": bool(GROWN_RE.search(t)),
        "larvae_oenocytes": bool(LARVA_RE.search(t)),
        "animation_as_science": bool(ANIM_RE.search(t)),
        "parent_f_restamp": bool(PARENT_F_RE.search(t)),
        "population_answers_circuit": bool(POP_CIRCUIT_RE.search(t)),
    }


def require_readme_clean(text: str) -> None:
    require_claims(**scan_text_flags(text), thread_id="readme")


__all__ = [
    "FLYWIRE_N",
    "MALECNS_N",
    "N_TEMPLATES_MAX",
    "SLICE_N_MAX",
    "LawBlockedError",
    "require_claims",
    "require_wiring",
    "require_engine",
    "require_templates",
    "require_assay_order",
    "require_readme_clean",
    "scan_text_flags",
]
