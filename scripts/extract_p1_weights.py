#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
"""Hop-1 signed synapses onto pC1 coexpress (P1-like) from named MaleCNS classes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data-raw"
OUT = ROOT / "data" / "templates"
PROV = ROOT / "data" / "templates" / "provenance.lock.json"

EXC = {"acetylcholine", "glutamate", "octopamine", "serotonin"}
INH = {"gaba"}
TARGET_MAX = 1.8  # scale so the strongest named |signed| onto P1 equals parent LC10a scale

LOCK_SHA = {
    "annotations.feather": "2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2",
    "neurotransmitters.feather": "95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621",
    "edges.feather": "5c536423a62a688e59e7b441f9c04d6272c9a1f017e35814cf561f8c275d9e9e",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def nt_sign(name: object) -> int:
    if name in EXC:
        return 1
    if name in INH:
        return -1
    return 0


def signed_hop1(w: pd.DataFrame, nt_s: pd.Series, pre: set[int], post: set[int]) -> dict:
    h = w[w["body_pre"].isin(pre) & w["body_post"].isin(post)]
    if h.empty:
        return {
            "n_edges": 0,
            "weight": 0,
            "signed": 0,
            "n_pre": 0,
            "n_post": 0,
            "nt": {},
        }
    nt = h["body_pre"].map(nt_s)
    sign = nt.map(nt_sign)
    return {
        "n_edges": int(len(h)),
        "weight": int(h["weight"].sum()),
        "signed": int((h["weight"] * sign).sum()),
        "n_pre": int(h["body_pre"].nunique()),
        "n_post": int(h["body_post"].nunique()),
        "nt": {str(k): int(v) for k, v in h.groupby(nt)["weight"].sum().items()},
    }


def main() -> None:
    for name, expect in LOCK_SHA.items():
        got = sha256(RAW / name)
        if got != expect:
            raise SystemExit(f"{name} sha256 {got} != {expect}")

    ann = pd.read_feather(RAW / "annotations.feather")
    nt = pd.read_feather(RAW / "neurotransmitters.feather").rename(columns={"body": "bodyId"})
    w = pd.read_feather(RAW / "edges.feather")
    type_s = ann["type"].fillna("").astype(str)
    fru = ann["fruDsx"].fillna("").astype(str)
    rt = ann["receptorType"].fillna("").astype(str)
    body = ann["bodyId"].astype("int64")
    sets = {
        "P1_coexpress": set(body[type_s.str.startswith("pC1_") & fru.str.startswith("coexpress")].astype(int)),
        "pC1_all": set(body[type_s.str.startswith("pC1_")].astype(int)),
        "ORN_DA1": set(body[type_s.eq("ORN_DA1")].astype(int)),
        "ORN_VA1v": set(body[type_s.eq("ORN_VA1v")].astype(int)),
        "VA1v_PN": set(body[type_s.isin(["VA1v_adPN", "VA1v_vPN"])].astype(int)),
        "DA1_PN": set(body[type_s.isin(["DA1_lPN", "DA1_vPN"])].astype(int)),
        "LC10a": set(body[type_s.eq("LC10a")].astype(int)),
        "ppk23": set(body[rt.eq("putative_ppk23")].astype(int)),
    }
    nt_s = nt.set_index("bodyId")["consensus_nt"]
    P1 = sets["P1_coexpress"]
    hops = {
        "VA1v_PN_to_P1": signed_hop1(w, nt_s, sets["VA1v_PN"], P1),
        "DA1_PN_to_P1": signed_hop1(w, nt_s, sets["DA1_PN"], P1),
        "LC10a_to_P1": signed_hop1(w, nt_s, sets["LC10a"], P1),
        "ppk23_to_P1": signed_hop1(w, nt_s, sets["ppk23"], P1),
        "ORN_VA1v_to_P1": signed_hop1(w, nt_s, sets["ORN_VA1v"], P1),
        "ORN_DA1_to_P1": signed_hop1(w, nt_s, sets["ORN_DA1"], P1),
        "ORN_DA1_to_DA1_PN": signed_hop1(w, nt_s, sets["ORN_DA1"], sets["DA1_PN"]),
        "ORN_VA1v_to_VA1v_PN": signed_hop1(w, nt_s, sets["ORN_VA1v"], sets["VA1v_PN"]),
        "DA1_PN_to_pC1": signed_hop1(w, nt_s, sets["DA1_PN"], sets["pC1_all"]),
        "LC10a_to_pC1": signed_hop1(w, nt_s, sets["LC10a"], sets["pC1_all"]),
    }
    named = {
        "ORN_HD": hops["VA1v_PN_to_P1"]["signed"],
        "DA1": hops["DA1_PN_to_P1"]["signed"],
        "LC10a": hops["LC10a_to_P1"]["signed"],
        "ppk23": hops["ppk23_to_P1"]["signed"],
    }
    peak = max(abs(v) for v in named.values()) or 1.0
    scale = peak / TARGET_MAX
    w_p1 = {k: round(v / scale, 4) for k, v in named.items()}
    cells = [
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
    ]
    n = len(cells)
    W = [[0.0] * n for _ in range(n)]
    # sensor / PN relays: schema self-weights so units can rise; ORN_cVA→DA1 path exists in MaleCNS
    W[0][0] = 0.15
    W[1][1] = 0.15
    W[2][1] = 1.5
    W[2][2] = 0.10
    W[3][3] = 0.10
    W[4][4] = 0.10
    W[5][5] = 0.15
    # P1 row: MaleCNS hop-1 signed, scaled. ppk23 is one class; f/m split is unused (both 0).
    W[6][0] = w_p1["ORN_HD"]
    W[6][2] = w_p1["DA1"]
    W[6][3] = w_p1["ppk23"]
    W[6][4] = w_p1["ppk23"]
    W[6][5] = w_p1["LC10a"]
    W[6][6] = 0.35
    # motor scaffolding remains schema (not hop-1 onto P1)
    W[7][6] = 1.00
    W[7][7] = 0.20
    W[8][6] = 1.10
    W[8][7] = 0.30
    W[8][8] = 0.15
    W[9][8] = 1.20
    W[9][9] = 0.20
    W[10][6] = 0.70
    W[10][7] = 0.20
    W[10][10] = 0.10
    extract = {
        "dataset": "male-cns:v1.0",
        "weights": "significant-only",
        "kind": "hop1_signed_onto_pC1_coexpress",
        "P1_definition": "type pC1_* and fruDsx coexpress_*",
        "n_P1": len(P1),
        "n_pC1": len(sets["pC1_all"]),
        "class_n": {k: len(v) for k, v in sets.items()},
        "hops": hops,
        "named_signed_onto_P1": named,
        "scale_divisor": scale,
        "target_max_abs": TARGET_MAX,
        "W_P1_named": w_p1,
        "holes": {
            "ppk23_hop1_onto_P1": hops["ppk23_to_P1"]["weight"] == 0,
            "ORN_HD_direct_onto_P1": hops["ORN_VA1v_to_P1"]["weight"] == 0,
            "DA1_hop1_sign": "acetylcholine_positive",
            "ppk23_f_m_split": "absent_in_map",
        },
    }
    spec = {
        "name": "malecns_p1_hop1",
        "sex": "male",
        "parent_map": "malecns_male",
        "parent_n": 166691,
        "female_parent_n": 139255,
        "kind": "hop1_signed_onto_pC1_coexpress",
        "citation": "Berg et al., Cell 2026. Hop-1 signed synapses onto pC1 coexpress. Not a 166,691-cell LIF.",
        "cells": cells,
        "sensors": ["ORN_HD", "ORN_cVA", "ppk23_f", "ppk23_m", "LC10a"],
        "readouts": {
            "P1": ["P1"],
            "orient": ["P1", "pC1"],
            "song": ["song_CPG"],
            "attempt": ["copulation"],
        },
        "W": W,
        "default_w_p1_da1": w_p1["DA1"],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "extract.json").write_text(json.dumps(extract, indent=2) + "\n", encoding="utf-8")
    (OUT / "male_p1.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    PROV.write_text(
        json.dumps(
            {
                "kind": "hop1_signed_onto_pC1_coexpress",
                "parent_male": {"map": "MaleCNS v1", "n": 166691, "citation": "Berg et al., Cell 2026"},
                "sha256": LOCK_SHA,
                "extract": True,
                "note": "Hop-1 signed sums onto pC1 coexpress. Motor rows are schema.",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("W_P1", w_p1, "scale", scale)
    print("wrote", OUT / "male_p1.json")


if __name__ == "__main__":
    main()
