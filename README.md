# fly_p1_sign

Do MaleCNS-derived signed weights onto P1/pC1 still make HD-on / cVA-off necessary and sufficient for the 3≈1 gate?

No. Hop-1 signed synapses onto pC1 coexpress do not. `hd_on_cva_off_ns` is false. Seed 1, 2,000 steps, `logs/p1_sign_s1.json`.

Parent [fly_icarus](https://github.com/martialsystems/fly_icarus) `@2cf5fd6` made HD-on / cVA-off necessary and sufficient on a published-sign slice (`W[P1, DA1] = -1.8`, 3d-pin `W_crit = -1.5262`). This tree replaces that P1 row with MaleCNS v1 hop-1 signed contact counts, scaled so the largest named |signed| onto P1 equals 1.8. Motor rows stay schema. Not a 166,691-cell LIF.

Hop-1 onto 88 pC1 coexpress cells:

| pre class | signed weight | scaled W onto P1 |
|-----------|--------------:|-----------------:|
| LC10a | +606 | 1.8 |
| DA1_lPN/vPN | +62 (acetylcholine) | 0.1842 |
| VA1v PNs (HD path) | -3 | -0.0089 |
| putative_ppk23 | 0 | 0 |

ORN_DA1 → DA1 PN is +32,016 (the cVA sensor path exists). Direct ORN → P1 is 0. ppk23 does not synapse onto P1 at hop-1. 3c equals 3d.

## Locked metrics

Copied from `logs/p1_sign_s1.json`.

| condition | P1 mean | DA1 term | LC10a term | song |
|-----------|--------:|---------:|-----------:|-----:|
| 1 flying female | 0.9207 | 0.0 | 1.2878 | 0.983 |
| 2 flying male | 0.7914 | 0.1529 | 0.6513 | 0.977 |
| 3 Icarus, HD | 0.9207 | 0.0 | 1.2874 | 0.983 |
| 3b Icarus, cVA | 0.9421 | 0.1535 | 1.2869 | 0.984 |
| 4 body only | 0.9219 | 0.0 | 1.2885 | 0.983 |
| 5 odor only | 0.7093 | 0.0 | 0.6479 | 0.973 |
| 6 Icarus female tag | 0.9207 | 0.0 | 1.2876 | 0.983 |
| 3c pin male cuticle | 0.9436 | 0.1544 | 1.2902 | 0.999 |
| 3d pin female cuticle | 0.9436 | 0.1544 | 1.2902 | 0.999 |
| copresent HD+cVA | 0.9413 | 0.1534 | 1.2864 | 0.984 |

3 tracks 1 (`d31 = 0.0`) because both are female-shaped LC10a. HD onto P1 is ~0. 3b is higher than 1: hop-1 DA1 is a weak accelerator. cVA does not reject. Every row sings. Seeds 2 and 3 match.

DA1 dose on the 3d pin (`logs/p1_da1_dose_s1.json`): extract default `W[P1, DA1] = +0.1842`, P1 = 0.9436. P1 crosses zero at `W[P1, DA1] = -1.539`. The map's hop-1 sign is on the court side of that crossing.

`--n 1000`, `--unfreeze`, and `--female-brain-icarus` stay stubbed.

Female template count: FlyWire 139,255. Male template count: MaleCNS 166,691.

## How to run

```
.venv/bin/python -m pytest
.venv/bin/python -m fly_p1_sign assay --seed 1 --steps 2000 --out logs/p1_sign_s1.json
.venv/bin/python -m fly_p1_sign da1-dose --seed 1 --steps 2000 --out logs/p1_da1_dose_s1.json
```

Rebuild W from feathers (optional):

```
.venv/bin/python scripts/extract_p1_weights.py
```

## Files

| Path | Role |
|------|------|
| `src/fly_p1_sign/` | Assay, hop-1 W, Icarus flag |
| `data/templates/extract.json` | Raw signed hop-1 sums |
| `data/templates/male_p1.json` | Scaled 11-cell W |
| `logs/p1_sign_s1.json` | Locked seed-1 battery |
| `logs/p1_da1_dose_s1.json` | 3d-pin DA1 sweep |
| `signforge/` | GraphForge pin |
| `AGENTS.md` | Project rules and VBD |
| `THIRD_PARTY.md` | Connectome attribution |

[Fly research index](https://gist.github.com/martialsystems/12835f747d6360781f3cc7f91f243178)
