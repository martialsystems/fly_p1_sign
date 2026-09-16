# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from fly_p1_sign.assay import AssayConfig, run_assay
from fly_p1_sign.cli import main


def test_n_1000_and_unfreeze_stubbed() -> None:
    assert main(["assay", "--n", "1000", "--steps", "10"]) == 2
    assert main(["assay", "--unfreeze", "--steps", "10"]) == 2


def test_hop1_battery_runs() -> None:
    result = run_assay(AssayConfig(seed=1, steps=400))
    rows = {str(r["condition"]): r for r in result["conditions"]}
    assert "3d" in rows and "3b" in rows
    assert result["engine"] == "hop1_signed_onto_pC1_coexpress"
    assert result["p1_term_weights"]["DA1"] == 0.1842
    ns = result["hd_cva_ns"]
    assert ns["present"] is True
    # hop-1 DA1 is +ACh and tiny; cVA is not a P1 brake
    assert rows["3b"]["p1_mean"] > 0.0
