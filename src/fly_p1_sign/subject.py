# Copyright (c) 2026 Martial Systems LLC
"""Male P1 slice: DA1, ppk23, LC10a live. Published-sign W, one shared template."""

from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np

from fly_p1_sign.paths import TEMPLATES
from signforge.gate import FLYWIRE_N, MALECNS_N, require_engine, require_templates

CELLS = (
    "ORN_HD",
    "ORN_cVA",
    "DA1",
    "ppk23_f",
    "ppk23_m",
    "LC10a",
    "P1",
    "pC1",
    "pIP10",
    "song_CPG",
    "copulation",
)

I_ORN_HD = 0
I_ORN_CVA = 1
I_DA1 = 2
I_PPK_F = 3
I_PPK_M = 4
I_LC10 = 5
I_P1 = 6
I_PC1 = 7
I_PIP10 = 8
I_SONG = 9
I_COP = 10

P1_TERM_CELLS = ("ORN_HD", "DA1", "ppk23_f", "ppk23_m", "LC10a", "P1")


def load_slice() -> dict:
    return json.loads((TEMPLATES / "male_p1.json").read_text(encoding="utf-8"))


_W: np.ndarray | None = None


def load_W() -> np.ndarray:
    global _W
    if _W is not None:
        return _W
    spec = load_slice()
    if spec["cells"] != list(CELLS):
        raise ValueError("male_p1.json cell order drifted")
    w = np.asarray(spec["W"], dtype=np.float64)
    if w.shape != (len(CELLS), len(CELLS)):
        raise ValueError(f"W shape {w.shape}")
    require_templates(
        female_n=int(spec["female_parent_n"]),
        male_n=int(spec["parent_n"]),
        slice_n=len(CELLS),
        unique_reconstruction=False,
        hop_count_extract=str(spec.get("kind") or "").startswith("hop1"),
    )
    require_engine(n_live_w=1, unique_w_per_fly=False)
    if spec["parent_n"] != MALECNS_N or spec["female_parent_n"] != FLYWIRE_N:
        raise ValueError("parent counts drifted")
    _W = w
    return w


@dataclass
class SubjectNet:
    W: np.ndarray
    r: np.ndarray

    @classmethod
    def fresh(cls) -> "SubjectNet":
        w = load_W()
        return cls(W=w, r=np.zeros(w.shape[0], dtype=np.float64))

    @classmethod
    def with_p1_da1_weight(cls, w_p1_da1: float) -> "SubjectNet":
        w = load_W().copy()
        w[I_P1, I_DA1] = float(w_p1_da1)
        return cls(W=w, r=np.zeros(w.shape[0], dtype=np.float64))

    def step(self, i_ext: np.ndarray) -> np.ndarray:
        self.r = np.tanh(self.W @ self.r + i_ext)
        return self.r

    @property
    def p1(self) -> float:
        return float(self.r[I_P1])

    @property
    def song(self) -> float:
        return float(self.r[I_SONG])

    @property
    def attempt(self) -> float:
        return float(self.r[I_COP])

    @property
    def orient(self) -> float:
        return float(0.5 * (self.r[I_P1] + self.r[I_PC1]))

    def p1_term_weights(self) -> dict[str, float]:
        return {name: float(self.W[I_P1, CELLS.index(name)]) for name in P1_TERM_CELLS}

    def p1_terms(self) -> dict[str, float]:
        """Weighted contributions to the P1 pre-activation from W[P1, :]."""
        return {
            name: float(self.W[I_P1, CELLS.index(name)] * self.r[CELLS.index(name)])
            for name in P1_TERM_CELLS
        }
