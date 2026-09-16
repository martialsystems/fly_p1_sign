# Copyright (c) 2026 Martial Systems LLC
"""Refuse laws. Verify-before-done is the finish gate."""

from __future__ import annotations

from typing import Any

from signforge.graphs.template_identity import FLYWIRE_N, MALECNS_N


def laws() -> list[dict[str, Any]]:
    from signforge.graphs.assay_order import build_graph as assay_order
    from signforge.graphs.claim_bans import build_graph as claim_bans
    from signforge.graphs.engine_shared import build_graph as engine_shared
    from signforge.graphs.template_identity import build_graph as template_identity
    from signforge.graphs.wiring_frozen import build_graph as wiring_frozen

    return [
        {
            "id": "sign.claim_bans",
            "build": claim_bans,
            "state": {
                "unique_brains": False,
                "population_spike_LIF": False,
                "grown_connectome": False,
                "larvae_oenocytes": False,
                "animation_as_science": False,
                "parent_f_restamp": False,
                "population_answers_circuit": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "sign.wiring_frozen",
            "build": wiring_frozen,
            "state": {"wiring_changed": False},
            "allow_decisions": ["allow"],
        },
        {
            "id": "sign.engine_shared",
            "build": engine_shared,
            "state": {
                "n_live_w": 1,
                "n_templates_max": 2,
                "unique_w_per_fly": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "sign.template_identity",
            "build": template_identity,
            "state": {
                "female_n": FLYWIRE_N,
                "male_n": MALECNS_N,
                "slice_n": 11,
                "unique_reconstruction": False,
                "hop_count_extract": True,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "sign.assay_order",
            "build": assay_order,
            "state": {
                "n": 2,
                "unfreeze": False,
                "female_brain_icarus": False,
                "exp1_passed": False,
            },
            "allow_decisions": ["allow"],
        },
    ]
