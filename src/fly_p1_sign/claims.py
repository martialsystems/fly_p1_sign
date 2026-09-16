# Copyright (c) 2026 Martial Systems LLC
"""Fail closed on banned claim tokens. Scan designated surfaces only."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from signforge.gate import scan_text_flags

BANNED: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("unique_brains", re.compile(r"unique reconstructed|1,?000 unique", re.I)),
    (
        "population_spike",
        re.compile(
            r"(default|population).{0,40}(full[- ]cns|139k|167k|166k).{0,20}spike|"
            r"live (whole-cns|139k|167k|166k) LIF",
            re.I,
        ),
    ),
    ("grown_connectome", re.compile(r"grew a (new )?connectome|grown connectome", re.I)),
    (
        "larvae_oenocytes",
        re.compile(r"\b(larva|larvae|oenocyte)s?\b.{0,40}\b(reconstr|map|connectome)", re.I),
    ),
    (
        "animation_as_science",
        re.compile(r"\b(animation|renderer)\b.{0,40}\b(science|result|finding)\b", re.I),
    ),
    ("parent_f_restamp", re.compile(r"F = 0\.524|IBD F = 0\.524", re.I)),
    (
        "schema_as_malecns_court",
        re.compile(r"MaleCNS P1 (would |does )?court|hop-count from the 166", re.I),
    ),
    ("males_court_fallen", re.compile(r"males court fallen", re.I)),
    ("shape_overrules_identity", re.compile(r"shape overrules identity", re.I)),
    ("unfreeze_licensed", re.compile(r"unfreeze is licensed", re.I)),
)


class ClaimBanError(RuntimeError):
    pass


def scan_text(text: str) -> list[str]:
    hits = [name for name, pat in BANNED if pat.search(text or "")]
    flags = scan_text_flags(text or "")
    for name, on in flags.items():
        if on and name not in hits:
            hits.append(name)
    return hits


def require_clean(text: str, *, source: str) -> None:
    hits = scan_text(text)
    if hits:
        raise ClaimBanError(f"{source}: banned claims {hits}")
    if "—" in (text or ""):
        raise ClaimBanError(f"{source}: em dash")


def require_paths_clean(paths: Iterable[Path]) -> None:
    for path in paths:
        if path.is_file():
            require_clean(path.read_text(encoding="utf-8"), source=str(path))
