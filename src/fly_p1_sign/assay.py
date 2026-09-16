# Copyright (c) 2026 Martial Systems LLC
"""Two-agent frozen-object assay. Same subject, object flags change."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass

import numpy as np

from fly_p1_sign.icarus import (
    CUTICLE_FEMALE,
    CUTICLE_MALE,
    ODOR_BOTH,
    ODOR_HD,
    ODOR_MALE,
    ODOR_NONE,
    Body,
    icarus_from_female,
    icarus_from_male,
    intact_female,
    intact_male,
)
from fly_p1_sign.metrics import (
    Acc,
    classify_3b,
    classify_3c,
    classify_3d,
    classify_copresent,
    classify_ns,
    classify_tag_leak,
    gate_looks_like_female,
)
from fly_p1_sign.odor import PIN_DISTANCE, contact_chc, dist, plume, visual_token
from fly_p1_sign.physics import DT, step_bodies
from fly_p1_sign.subject import (
    I_LC10,
    I_ORN_CVA,
    I_ORN_HD,
    I_PPK_F,
    I_PPK_M,
    CELLS,
    P1_TERM_CELLS,
    SubjectNet,
)
from signforge.gate import require_assay_order, require_engine

CONDITION_NAMES = {
    "1": "flying_female",
    "2": "flying_male",
    "3": "icarus_from_male",
    "3b": "icarus_from_male_male_odor",
    "4": "icarus_from_male_body_only",
    "5": "icarus_from_male_odor_only",
    "6": "icarus_from_female",
    "3c": "icarus_pin_male_cuticle",
    "3d": "icarus_pin_female_cuticle",
    "copresent": "icarus_hd_and_cva",
}

CONDITION_ROLES = {
    "1": "positive control",
    "2": "negative control",
    "3": "the rule: fat wingless, HD on",
    "3b": "Icarus body, odor still male (cVA on, HD off), free approach",
    "4": "morphology without 7,11-HD",
    "5": "7,11-HD without the fat wingless female shape",
    "6": "same body+odor as 3, female wiring tag",
    "3c": "forced contact, Icarus body, male odor, male cuticle",
    "3d": "forced contact, Icarus body, male odor, female cuticle",
    "copresent": "Icarus body, HD and cVA both on, free approach",
}

DEFAULT_CONDITIONS = (
    "1",
    "2",
    "3",
    "3b",
    "4",
    "5",
    "6",
    "3c",
    "3d",
    "copresent",
)
MALE_ICARUS = {"3", "3b", "4", "5", "3c", "3d", "copresent"}
PINNED = {"3c", "3d"}


@dataclass
class AssayConfig:
    seed: int = 1
    steps: int = 2000
    conditions: tuple[str, ...] = DEFAULT_CONDITIONS
    start_x: float = 6.0
    record_frames: bool = False
    frame_stride: int = 10


def _cid(condition: str | int) -> str:
    return str(condition)


def make_object(condition: str | int) -> Body:
    c = _cid(condition)
    if c == "1":
        return intact_female(frozen=True)
    if c == "2":
        return intact_male(frozen=True)
    if c == "3":
        return icarus_from_male(odor=ODOR_HD, female_body=True)
    if c == "3b":
        return icarus_from_male(odor=ODOR_MALE, female_body=True)
    if c == "4":
        return icarus_from_male(odor=ODOR_NONE, female_body=True)
    if c == "5":
        return icarus_from_male(odor=ODOR_HD, female_body=False)
    if c == "6":
        return icarus_from_female(odor=ODOR_HD, female_body=True)
    if c == "3c":
        return icarus_from_male(odor=ODOR_MALE, female_body=True, cuticle=CUTICLE_MALE)
    if c == "3d":
        return icarus_from_male(odor=ODOR_MALE, female_body=True, cuticle=CUTICLE_FEMALE)
    if c == "copresent":
        return icarus_from_male(odor=ODOR_BOTH, female_body=True, cuticle=CUTICLE_MALE)
    raise ValueError(f"unknown condition {condition!r}")


def make_subject(cfg: AssayConfig, rng: np.random.Generator) -> Body:
    jitter = float(rng.normal(0.0, 0.15))
    heading = float(rng.uniform(-0.2, 0.2))
    return Body(
        x=cfg.start_x,
        y=jitter,
        heading=heading,
        wiring_sex=1,
        wings=True,
        mass=1.0,
        abdomen="male",
        odor="male",
        cuticle="male",
        frozen=False,
        icarus=False,
    )


def sensory_current(subject: Body, obj: Body) -> np.ndarray:
    d = dist(subject, obj)
    hd, cva = plume(obj, d)
    vis = visual_token(obj, d)
    pk_f, pk_m = contact_chc(obj, d)
    i = np.zeros(len(CELLS), dtype=np.float64)
    i[I_ORN_HD] = hd
    i[I_ORN_CVA] = cva
    i[I_PPK_F] = pk_f
    i[I_PPK_M] = pk_m
    i[I_LC10] = vis
    return i


def run_condition(
    condition: str | int,
    cfg: AssayConfig,
    rng: np.random.Generator,
    *,
    da1_weight: float | None = None,
) -> dict:
    c = _cid(condition)
    obj = make_object(c)
    if obj.frozen is False:
        raise RuntimeError("object must be frozen in experiment 1")
    if c in MALE_ICARUS and obj.wiring_sex != 1:
        raise RuntimeError("Icarus-from-male swapped wiring_sex")
    if c == "6" and obj.wiring_sex != 0:
        raise RuntimeError("Icarus-from-female lost female wiring tag")
    subject = make_subject(cfg, rng)
    pin = c in PINNED
    if pin:
        subject.x = PIN_DISTANCE
        subject.y = 0.0
        subject.heading = math.pi
    net = (
        SubjectNet.fresh()
        if da1_weight is None
        else SubjectNet.with_p1_da1_weight(da1_weight)
    )
    acc = Acc()
    frames: list[dict] = []
    x0, y0 = subject.x, subject.y
    for t in range(cfg.steps):
        d = dist(subject, obj)
        net.step(sensory_current(subject, obj))
        st = step_bodies(subject, obj, net, d, pin=pin)
        if pin and (subject.x != x0 or subject.y != y0):
            raise RuntimeError("pinned subject walked")
        terms = net.p1_terms()
        acc.tick(
            p1=float(st["p1"]),
            aligned=bool(st["aligned"]),
            singing=bool(st["singing"]),
            trying=bool(st["trying"]),
            terms=terms,
        )
        if cfg.record_frames and t % cfg.frame_stride == 0:
            frames.append(
                {
                    "t": round(t * DT, 3),
                    "sx": round(subject.x, 3),
                    "sy": round(subject.y, 3),
                    "sh": round(subject.heading, 3),
                    "p1": round(float(st["p1"]), 3),
                    "song": int(bool(st["singing"])),
                }
            )
    out = {
        "condition": c,
        "name": CONDITION_NAMES[c],
        "role": CONDITION_ROLES[c],
        "object": {
            "wiring_sex": int(obj.wiring_sex),
            "wings": bool(obj.wings),
            "abdomen": obj.abdomen,
            "odor": obj.odor,
            "cuticle": obj.cuticle,
            "icarus": bool(obj.icarus),
            "frozen": bool(obj.frozen),
            "mass": obj.mass,
        },
        "pin": pin,
        **acc.summary(),
    }
    if frames:
        out["frames"] = frames
    return out


def run_assay(cfg: AssayConfig) -> dict:
    require_assay_order(n=2, unfreeze=False, female_brain_icarus=False, exp1_passed=False)
    require_engine(n_live_w=1, unique_w_per_fly=False)
    rng = np.random.default_rng(cfg.seed)
    rows: dict[str, dict] = {}
    ordered = []
    weights = None
    for c in cfg.conditions:
        cid = _cid(c)
        row = run_condition(cid, cfg, rng)
        rows[cid] = row
        ordered.append(row)
        if weights is None:
            weights = SubjectNet.fresh().p1_term_weights()
    gate = (
        gate_looks_like_female(rows)
        if {"1", "2", "3"} <= set(rows)
        else {"passed": False, "rule": "missing 1-3"}
    )
    return {
        "schema": "fly_p1_sign.v1",
        "question": (
            "Do MaleCNS-derived signed weights onto P1/pC1 still make HD-on / cVA-off "
            "necessary and sufficient for the 3≈1 gate?"
        ),
        "honesty": (
            "Hop-1 signed synapses onto pC1 coexpress from MaleCNS v1 significant-only. "
            "Motor rows are schema. Not a 166,691-cell LIF. Parent fly_icarus @2cf5fd6 "
            "is the published-sign slice."
        ),
        "n_agents": 2,
        "n_live_w": 1,
        "seed": cfg.seed,
        "steps": cfg.steps,
        "dt": DT,
        "engine": "hop1_signed_onto_pC1_coexpress",
        "parent_female_n": 139255,
        "parent_male_n": 166691,
        "slice_n": len(CELLS),
        "p1_term_cells": list(P1_TERM_CELLS),
        "p1_term_weights": weights,
        "conditions": ordered,
        "gate": gate,
        "control_3b": classify_3b(rows),
        "tag_leak": classify_tag_leak(rows),
        "control_3c": classify_3c(rows),
        "control_3d": classify_3d(rows),
        "copresent": classify_copresent(rows),
        "hd_cva_ns": classify_ns(rows),
    }


def write_run(result: dict, path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
