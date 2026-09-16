# Copyright (c) 2026 Martial Systems LLC
"""CLI for the two-agent frozen P1 assay."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fly_p1_sign.assay import AssayConfig, run_assay, write_run
from fly_p1_sign.dose import run_da1_dose
from fly_p1_sign.claims import require_clean
from fly_p1_sign.paths import LOGS, REPO
from signforge.gate import LawBlockedError, require_assay_order, require_readme_clean

BANNER = (
    "Two agents. MaleCNS hop-1 signed weights onto pC1 coexpress. "
    "Frozen object. Wiring stays. Not a 166,691-cell LIF."
)

LOCK_NAME = "p1_sign_s1.json"


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="fly-p1-sign", description=BANNER)
    sub = p.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser(
        "assay",
        help="run frozen-object assay including 3c/3d/copresent. Unfreeze stays stubbed.",
    )
    run.add_argument("--seed", type=int, default=1)
    run.add_argument("--steps", type=int, default=2000)
    run.add_argument("--out", type=Path, default=LOGS / "p1_terms.json")
    run.add_argument("--frames", action="store_true")
    run.add_argument("--n", type=int, default=2)
    run.add_argument("--unfreeze", action="store_true")
    run.add_argument("--female-brain-icarus", action="store_true")
    dose = sub.add_parser(
        "da1-dose",
        help="sweep W[P1,DA1] on the 3d pin until P1 mean crosses zero",
    )
    dose.add_argument("--seed", type=int, default=1)
    dose.add_argument("--steps", type=int, default=2000)
    dose.add_argument("--out", type=Path, default=LOGS / "p1_da1_dose.json")
    dose.add_argument("--n", type=int, default=2)
    dose.add_argument("--unfreeze", action="store_true")
    dose.add_argument("--female-brain-icarus", action="store_true")
    return p


def _exp1_passed() -> bool:
    lock = LOGS / LOCK_NAME
    if not lock.is_file():
        return False
    try:
        data = json.loads(lock.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return bool((data.get("gate") or {}).get("passed"))


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    require_clean(BANNER, source="banner")
    readme = REPO / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        require_readme_clean(text)
        require_clean(text, source="README.md")
    try:
        require_assay_order(
            n=int(args.n),
            unfreeze=bool(args.unfreeze),
            female_brain_icarus=bool(args.female_brain_icarus),
            exp1_passed=_exp1_passed(),
        )
    except LawBlockedError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    if int(args.n) != 2 or bool(args.unfreeze) or bool(args.female_brain_icarus):
        print("experiment 2/3 is stubbed until the frozen assay is the lock", file=sys.stderr)
        return 2
    if args.cmd == "da1-dose":
        cfg = AssayConfig(seed=int(args.seed), steps=int(args.steps))
        result = run_da1_dose(cfg)
        write_run(result, args.out)
        crit = result.get("critical_weight") or {}
        print(
            f"seed={result['seed']} steps={result['steps']} "
            f"default_w={result['default_w_p1_da1']} "
            f"p1_at_default={result['p1_at_default']} "
            f"crossed={crit.get('crossed')} w_crit={crit.get('w_p1_da1')}"
        )
        return 0 if crit.get("crossed") else 1
    if args.cmd != "assay":
        return 1
    cfg = AssayConfig(
        seed=int(args.seed),
        steps=int(args.steps),
        record_frames=bool(args.frames),
    )
    result = run_assay(cfg)
    write_run(result, args.out)
    gate = result["gate"]
    c3b = result.get("control_3b") or {}
    c3c = result.get("control_3c") or {}
    c3d = result.get("control_3d") or {}
    cop = result.get("copresent") or {}
    leak = result.get("tag_leak") or {}
    print(
        f"seed={result['seed']} steps={result['steps']} "
        f"gate={gate['passed']} d31={gate.get('d31')} d32={gate.get('d32')} "
        f"3b={c3b.get('driver')} 3c_male_taste={c3c.get('male_taste_on')} "
        f"3d={c3d.get('driver')} copresent_both={cop.get('both_ligands')} "
        f"tag_leak_matched={leak.get('matched')} "
        f"hd_cva_ns={(result.get('hd_cva_ns') or {}).get('hd_on_cva_off_ns')}"
    )
    for row in result["conditions"]:
        terms = row.get("p1_terms") or {}
        print(
            f"  {row['condition']} {row['name']}: "
            f"P1={row['p1_mean']:.3f} orient={row['orient_frac']:.3f} "
            f"song={row['song_frac']:.3f} bouts={row['song_bouts']} "
            f"onset={row.get('song_onset_step')} "
            f"attempts={row['copulation_attempts']} "
            f"terms HD={terms.get('ORN_HD')} DA1={terms.get('DA1')} "
            f"ppk_f={terms.get('ppk23_f')} ppk_m={terms.get('ppk23_m')} "
            f"LC10a={terms.get('LC10a')} latch={terms.get('P1')}"
        )
    return 0 if gate["passed"] else 1
