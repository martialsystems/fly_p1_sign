# Copyright (c) 2026 Martial Systems LLC
"""P1 rate, orientation time, song bouts, copulation attempts, P1 term columns."""

from __future__ import annotations

from dataclasses import dataclass, field

from fly_p1_sign.subject import P1_TERM_CELLS


@dataclass
class Acc:
    n: int = 0
    p1_sum: float = 0.0
    orient_ticks: int = 0
    song_ticks: int = 0
    song_bouts: int = 0
    attempts: int = 0
    song_onset_step: int | None = None
    _song_on: bool = False
    _try_on: bool = False
    p1_series: list[float] = field(default_factory=list)
    term_sum: dict[str, float] = field(
        default_factory=lambda: {name: 0.0 for name in P1_TERM_CELLS}
    )

    def tick(
        self,
        *,
        p1: float,
        aligned: bool,
        singing: bool,
        trying: bool,
        terms: dict[str, float] | None = None,
    ) -> None:
        self.n += 1
        self.p1_sum += float(p1)
        if aligned:
            self.orient_ticks += 1
        if singing:
            self.song_ticks += 1
            if not self._song_on:
                self.song_bouts += 1
                if self.song_onset_step is None:
                    self.song_onset_step = self.n - 1
            self._song_on = True
        else:
            self._song_on = False
        if trying:
            if not self._try_on:
                self.attempts += 1
            self._try_on = True
        else:
            self._try_on = False
        if terms:
            for name in P1_TERM_CELLS:
                self.term_sum[name] += float(terms.get(name, 0.0))
        if len(self.p1_series) < 400 or self.n % 5 == 0:
            self.p1_series.append(round(float(p1), 4))

    def summary(self) -> dict:
        n = max(self.n, 1)
        terms = {name: round(self.term_sum[name] / n, 4) for name in P1_TERM_CELLS}
        terms["sum"] = round(sum(terms[name] for name in P1_TERM_CELLS), 4)
        return {
            "steps": self.n,
            "p1_mean": round(self.p1_sum / n, 4),
            "orient_frac": round(self.orient_ticks / n, 4),
            "song_frac": round(self.song_ticks / n, 4),
            "song_bouts": int(self.song_bouts),
            "song_onset_step": self.song_onset_step,
            "copulation_attempts": int(self.attempts),
            "p1_terms": terms,
        }


def gate_looks_like_female(rows: dict[str, dict]) -> dict:
    """Condition 3 with 1, not with 2, on song and orientation."""
    a = rows["1"]
    b = rows["2"]
    c = rows["3"]
    d31 = abs(c["song_frac"] - a["song_frac"]) + abs(c["orient_frac"] - a["orient_frac"])
    d32 = abs(c["song_frac"] - b["song_frac"]) + abs(c["orient_frac"] - b["orient_frac"])
    p1_31 = abs(c["p1_mean"] - a["p1_mean"])
    p1_32 = abs(c["p1_mean"] - b["p1_mean"])
    passed = (
        d31 < d32
        and p1_31 < p1_32
        and c["song_frac"] > b["song_frac"]
        and a["song_frac"] > b["song_frac"]
        and c["p1_mean"] > b["p1_mean"]
        and a["p1_mean"] > 0.2
    )
    return {
        "passed": bool(passed),
        "d31": round(d31, 4),
        "d32": round(d32, 4),
        "p1_d31": round(p1_31, 4),
        "p1_d32": round(p1_32, 4),
        "rule": (
            "condition 3 closer to 1 than to 2 on song, orient, and P1; "
            "schema-gate only, same signed channels into a saturating unit"
        ),
    }


def classify_3b(rows: dict[str, dict]) -> dict:
    """Icarus body with male odor: odor rewrite vs shape overruling cVA."""
    if "3b" not in rows:
        return {"present": False}
    b = rows["3b"]
    c2 = rows["2"]
    c3 = rows["3"]
    d_b2 = abs(b["p1_mean"] - c2["p1_mean"])
    d_b3 = abs(b["p1_mean"] - c3["p1_mean"])
    if d_b2 < d_b3 and b["p1_mean"] < 0.0:
        driver = "odor_rewrite"
    elif d_b3 < d_b2 and b["p1_mean"] > 0.0:
        driver = "shape_overrules_cva"
    else:
        driver = "mixed"
    return {
        "present": True,
        "p1_mean": b["p1_mean"],
        "d_3b_2": round(d_b2, 4),
        "d_3b_3": round(d_b3, 4),
        "driver": driver,
    }


def classify_tag_leak(rows: dict[str, dict]) -> dict:
    """Condition 6 vs 3: frozen object, same body+odor, female vs male tag."""
    if "6" not in rows or "3" not in rows:
        return {"present": False}
    d36 = abs(rows["6"]["p1_mean"] - rows["3"]["p1_mean"])
    return {
        "present": True,
        "p1_d36": round(d36, 4),
        "matched": bool(d36 < 0.02),
    }


def classify_3c(rows: dict[str, dict]) -> dict:
    """Pinned Icarus body, male odor, male cuticle. Taste should brake further."""
    if "3c" not in rows:
        return {"present": False}
    c = rows["3c"]
    b = rows.get("3b")
    terms = c.get("p1_terms") or {}
    more_neg = None if b is None else bool(c["p1_mean"] < b["p1_mean"])
    return {
        "present": True,
        "p1_mean": c["p1_mean"],
        "ppk23_m": terms.get("ppk23_m"),
        "ppk23_f": terms.get("ppk23_f"),
        "more_negative_than_3b": more_neg,
        "male_taste_on": bool(float(terms.get("ppk23_m") or 0.0) < -0.4),
    }


def classify_3d(rows: dict[str, dict]) -> dict:
    """Pinned Icarus body, male odor, female cuticle. Can shape-plus-taste beat DA1?"""
    if "3d" not in rows:
        return {"present": False}
    d = rows["3d"]
    terms = d.get("p1_terms") or {}
    p1 = float(d["p1_mean"])
    if p1 > 0.0:
        driver = "contact_feminize_required"
    else:
        driver = "da1_wins_full_excitatory_bundle"
    return {
        "present": True,
        "p1_mean": d["p1_mean"],
        "ppk23_f": terms.get("ppk23_f"),
        "ppk23_m": terms.get("ppk23_m"),
        "DA1": terms.get("DA1"),
        "LC10a": terms.get("LC10a"),
        "driver": driver,
    }


def classify_ns(rows: dict[str, dict]) -> dict:
    """HD-on / cVA-off is N&S only if 3 tracks 1 and 3b tracks 2 (cVA rejects)."""
    if not {"1", "2", "3", "3b"} <= set(rows):
        return {"present": False}
    d31 = abs(rows["3"]["p1_mean"] - rows["1"]["p1_mean"])
    d3b1 = abs(rows["3b"]["p1_mean"] - rows["1"]["p1_mean"])
    d3b2 = abs(rows["3b"]["p1_mean"] - rows["2"]["p1_mean"])
    three_like_one = d31 < abs(rows["3"]["p1_mean"] - rows["2"]["p1_mean"])
    cva_rejects = rows["3b"]["p1_mean"] < 0.0 and d3b2 < d3b1
    return {
        "present": True,
        "d31": round(d31, 4),
        "d3b_1": round(d3b1, 4),
        "d3b_2": round(d3b2, 4),
        "three_like_one": bool(three_like_one),
        "cva_rejects": bool(cva_rejects),
        "hd_on_cva_off_ns": bool(three_like_one and cva_rejects),
    }


def classify_copresent(rows: dict[str, dict]) -> dict:
    """Icarus body, HD and cVA both on, free approach."""
    if "copresent" not in rows:
        return {"present": False}
    r = rows["copresent"]
    terms = r.get("p1_terms") or {}
    return {
        "present": True,
        "p1_mean": r["p1_mean"],
        "ORN_HD": terms.get("ORN_HD"),
        "DA1": terms.get("DA1"),
        "song_frac": r["song_frac"],
        "both_ligands": bool(
            float(terms.get("ORN_HD") or 0.0) > 0.05
            and float(terms.get("DA1") or 0.0) < -0.05
        ),
    }
