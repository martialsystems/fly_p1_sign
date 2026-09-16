# Copyright (c) 2026 Martial Systems LLC
"""Icarus is a morphology and odor flag. It does not swap wiring_sex."""

from __future__ import annotations

from dataclasses import dataclass, replace

from signforge.gate import require_wiring

FEMALE = 0
MALE = 1

ODOR_NONE = "none"
ODOR_HD = "hd"
ODOR_MALE = "male"
ODOR_BOTH = "both"

CUTICLE_NONE = "none"
CUTICLE_MALE = "male"
CUTICLE_FEMALE = "female"

ABDOMEN_MALE = "male"
ABDOMEN_FEMALE = "female"

ODORS = (ODOR_NONE, ODOR_HD, ODOR_MALE, ODOR_BOTH)
CUTICLES = (CUTICLE_NONE, CUTICLE_MALE, CUTICLE_FEMALE)


def default_cuticle(odor: str) -> str:
    if odor == ODOR_HD:
        return CUTICLE_FEMALE
    if odor == ODOR_MALE:
        return CUTICLE_MALE
    if odor == ODOR_BOTH:
        return CUTICLE_MALE
    return CUTICLE_NONE

MALE_MASS = 1.0
FEMALE_MASS = 1.35
ICARUS_MASS = 1.8


@dataclass
class Body:
    x: float
    y: float
    heading: float
    wiring_sex: int
    wings: bool
    mass: float
    abdomen: str
    odor: str
    cuticle: str
    frozen: bool
    icarus: bool


def intact_female(*, x: float = 0.0, y: float = 0.0, frozen: bool = True) -> Body:
    return Body(
        x=x,
        y=y,
        heading=0.0,
        wiring_sex=FEMALE,
        wings=True,
        mass=FEMALE_MASS,
        abdomen=ABDOMEN_FEMALE,
        odor=ODOR_HD,
        cuticle=CUTICLE_FEMALE,
        frozen=frozen,
        icarus=False,
    )


def intact_male(*, x: float = 0.0, y: float = 0.0, frozen: bool = True) -> Body:
    return Body(
        x=x,
        y=y,
        heading=0.0,
        wiring_sex=MALE,
        wings=True,
        mass=MALE_MASS,
        abdomen=ABDOMEN_MALE,
        odor=ODOR_MALE,
        cuticle=CUTICLE_MALE,
        frozen=frozen,
        icarus=False,
    )


def apply_icarus(
    body: Body,
    *,
    odor: str = ODOR_HD,
    female_body: bool = True,
    cuticle: str | None = None,
) -> Body:
    """House rule. Wiring sex is copied, never rewritten.

    odor is a volatile source: hd, male (cVA / 7-T), both, or none.
    cuticle is contact CHC and is independent of the plume. Default cuticle
    follows odor so 1 to 6 stay the old coupling.
    """
    if odor not in ODORS:
        raise ValueError(f"unknown odor {odor!r}")
    chc = default_cuticle(odor) if cuticle is None else cuticle
    if chc not in CUTICLES:
        raise ValueError(f"unknown cuticle {chc!r}")
    wiring = int(body.wiring_sex)
    out = replace(
        body,
        icarus=True,
        wings=False,
        mass=ICARUS_MASS,
        abdomen=ABDOMEN_FEMALE if female_body else ABDOMEN_MALE,
        odor=odor,
        cuticle=chc,
        frozen=True,
        wiring_sex=wiring,
    )
    require_wiring(wiring_changed=out.wiring_sex != wiring)
    return out


def icarus_from_male(
    *,
    odor: str = ODOR_HD,
    female_body: bool = True,
    cuticle: str | None = None,
) -> Body:
    return apply_icarus(intact_male(), odor=odor, female_body=female_body, cuticle=cuticle)


def icarus_from_female(
    *,
    odor: str = ODOR_HD,
    female_body: bool = True,
    cuticle: str | None = None,
) -> Body:
    return apply_icarus(
        intact_female(), odor=odor, female_body=female_body, cuticle=cuticle
    )
