# Agent notes: fly_p1_sign

MIT for original code. FlyWire and MaleCNS remain under their published licenses (typically CC BY 4.0).

Question: Do MaleCNS-derived signed weights onto P1/pC1 still make HD-on / cVA-off necessary and sufficient for the 3≈1 gate?

Parent `fly_icarus` `@2cf5fd6` is closed. Do not restamp its locks or W_crit = -1.5262 as this tree's weight. Do not reopen `p1_contact_s1.json`. Unfreeze stays stubbed.

W is hop-1 signed synapses onto type `pC1_*` with `fruDsx` coexpress, from DA1 PNs, LC10a, VA1v PNs, and putative_ppk23. Scale so max |named signed| onto P1 equals 1.8. Motor scaffolding is schema. Slice is 11 cells.

Pin is `signforge/`. Hop-1 extract is required. Unique reconstruction is refused. Verify-before-done is the finish gate.

## Verify

`python3 ~/agent_laws_verify_before_done/vbd_gate.py check --app-root . --claim-done`

Do not use stock `/usr/bin/python3 -m pytest`.
