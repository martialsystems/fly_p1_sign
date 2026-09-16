# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import json
from pathlib import Path

from fly_p1_sign.claims import scan_text

REPO = Path(__file__).resolve().parents[1]
LOCK = REPO / "logs" / "p1_sign_s1.json"
QUESTION = (
    "Do MaleCNS-derived signed weights onto P1/pC1 still make HD-on / cVA-off "
    "necessary and sufficient for the 3≈1 gate?"
)


def test_readme_question_first() -> None:
    text = (REPO / "README.md").read_text(encoding="utf-8")
    assert text.startswith("# fly_p1_sign\n")
    body = text.split("\n", 1)[1].lstrip()
    assert body.startswith(QUESTION)
    assert "What it is not" not in text
    assert "—" not in text
    assert scan_text(text) == []
    assert "139,255" in text
    assert "166,691" in text
    assert ".venv/bin/python -m pytest" in text
    assert "signforge/" in text
    assert "https://gist.github.com/martialsystems/12835f747d6360781f3cc7f91f243178" in text
    assert "@2cf5fd6" in text
    desc = (REPO / "description.txt").read_text(encoding="utf-8")
    assert desc.startswith(QUESTION.split(" still")[0]) or QUESTION[:40] in desc
    assert "—" not in desc
    assert scan_text(desc) == []


def test_lock_numbers_in_readme() -> None:
    data = json.loads(LOCK.read_text(encoding="utf-8"))
    text = (REPO / "README.md").read_text(encoding="utf-8")
    assert data["question"] == QUESTION
    assert data["hd_cva_ns"]["hd_on_cva_off_ns"] is False
    rows = {str(r["condition"]): r for r in data["conditions"]}
    assert str(rows["3"]["p1_mean"]) in text
    assert str(rows["3b"]["p1_mean"]) in text
    assert str(rows["3d"]["p1_mean"]) in text
    dose = json.loads((REPO / "logs" / "p1_da1_dose_s1.json").read_text())
    assert str(dose["critical_weight"]["w_p1_da1"]) in text
    assert str(dose["default_w_p1_da1"]) in text
