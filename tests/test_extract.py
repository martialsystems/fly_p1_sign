# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_extract_da1_is_weak_and_positive() -> None:
    ext = json.loads((REPO / "data" / "templates" / "extract.json").read_text())
    assert ext["kind"] == "hop1_signed_onto_pC1_coexpress"
    assert ext["named_signed_onto_P1"]["DA1"] == 62
    assert ext["named_signed_onto_P1"]["LC10a"] == 606
    assert ext["named_signed_onto_P1"]["ppk23"] == 0
    assert ext["holes"]["ppk23_hop1_onto_P1"] is True
    spec = json.loads((REPO / "data" / "templates" / "male_p1.json").read_text())
    assert spec["W"][6][2] == 0.1842
    assert spec["W"][6][5] == 1.8
    assert spec["W"][6][3] == 0.0
    assert spec["default_w_p1_da1"] == 0.1842
    assert spec["parent_n"] == 166691
