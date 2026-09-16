# Copyright (c) 2026 Martial Systems LLC
"""Two-body box. Object freeze holds. Subject orients and walks from P1."""

from __future__ import annotations

import math

from fly_p1_sign.icarus import Body
from fly_p1_sign.odor import COP_RADIUS, bearing, heading_error, wrap_angle
from fly_p1_sign.subject import SubjectNet

DT = 0.05
TURN = 5.0
WALK = 2.2
ORIENT_THRESH = 0.22
APPROACH_THRESH = 0.28
SONG_THRESH = 0.38
ATTEMPT_THRESH = 0.48
ORIENT_ALIGN = 0.55


def _clip_arena(body: Body, half: float = 12.0) -> None:
    body.x = max(-half, min(half, body.x))
    body.y = max(-half, min(half, body.y))


def step_bodies(
    subject: Body,
    obj: Body,
    net: SubjectNet,
    d: float,
    *,
    pin: bool = False,
) -> dict[str, float | bool]:
    """Advance the subject. Frozen objects do not move and do not court.

    pin: hold the subject at attempt range. P1 does not decide whether they close.
    """
    if obj.frozen:
        obj.heading = obj.heading
    else:
        raise RuntimeError("experiment 1 object must stay frozen")

    orient = net.orient
    song = net.song
    attempt = net.attempt
    p1 = net.p1
    if pin:
        subject.heading = bearing(subject, obj)
        err = 0.0
        aligned = p1 > ORIENT_THRESH
    else:
        err = heading_error(subject, obj)
        aligned = abs(err) < ORIENT_ALIGN and p1 > ORIENT_THRESH
        if p1 > ORIENT_THRESH:
            subject.heading = wrap_angle(
                subject.heading + DT * TURN * math.tanh(p1) * err
            )
        if p1 > APPROACH_THRESH and aligned and d > COP_RADIUS * 0.6:
            subject.x += DT * WALK * min(p1, 1.0) * math.cos(subject.heading)
            subject.y += DT * WALK * min(p1, 1.0) * math.sin(subject.heading)
        _clip_arena(subject)

    singing = song > SONG_THRESH and d < 4.0
    trying = attempt > ATTEMPT_THRESH and d < COP_RADIUS
    return {
        "p1": p1,
        "orient": orient,
        "song": song,
        "attempt": attempt,
        "aligned": aligned,
        "singing": singing,
        "trying": trying,
        "err": err,
        "d": d,
    }
