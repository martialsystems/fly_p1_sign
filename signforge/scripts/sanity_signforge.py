#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
"""Refuse paths for signforge laws."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from signforge.gate import (
    FLYWIRE_N,
    MALECNS_N,
    LawBlockedError,
    require_assay_order,
    require_claims,
    require_engine,
    require_templates,
    require_wiring,
)


def main() -> None:
    require_claims()
    try:
        require_claims(unique_brains=True)
        raise SystemExit("expected unique_brains block")
    except LawBlockedError:
        pass
    try:
        require_claims(population_answers_circuit=True)
        raise SystemExit("expected population_answers_circuit block")
    except LawBlockedError:
        pass

    require_wiring(wiring_changed=False)
    try:
        require_wiring(wiring_changed=True)
        raise SystemExit("expected wiring_changed block")
    except LawBlockedError:
        pass

    require_engine(n_live_w=1)
    try:
        require_engine(n_live_w=1, unique_w_per_fly=True)
        raise SystemExit("expected unique_w_per_fly block")
    except LawBlockedError:
        pass
    try:
        require_engine(n_live_w=3)
        raise SystemExit("expected too many W block")
    except LawBlockedError:
        pass

    require_templates(female_n=FLYWIRE_N, male_n=MALECNS_N, slice_n=11, hop_count_extract=True)
    try:
        require_templates(
            female_n=FLYWIRE_N,
            male_n=MALECNS_N,
            slice_n=11,
            unique_reconstruction=True,
            hop_count_extract=True,
        )
        raise SystemExit("expected unique_reconstruction block")
    except LawBlockedError:
        pass
    try:
        require_templates(female_n=FLYWIRE_N, male_n=MALECNS_N, slice_n=11, hop_count_extract=False)
        raise SystemExit("expected need_hop_extract block")
    except LawBlockedError:
        pass

    require_assay_order(n=2, unfreeze=False, exp1_passed=False)
    try:
        require_assay_order(n=1000, exp1_passed=False)
        raise SystemExit("expected n_before_exp1 block")
    except LawBlockedError:
        pass
    try:
        require_assay_order(n=2, unfreeze=True, exp1_passed=False)
        raise SystemExit("expected unfreeze_before_exp1 block")
    except LawBlockedError:
        pass
    require_assay_order(n=2, unfreeze=True, exp1_passed=True)
    print("signforge sanity ok")


if __name__ == "__main__":
    main()
