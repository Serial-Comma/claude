#!/usr/bin/env python3
"""TomTom live-traffic calibration sample (20 routes, 5 per distance band).
Captured 2026-09-17 ~18:43-18:46 SGT (Thursday evening) -- an off-peak-evening
live snapshot, NOT the target 07:00-07:30 AM school-commute window. OneMap has
no traffic model at all (free-flow only), so this is the best real-world
signal obtainable for how much congestion actually inflates drive time on
these specific routes, used here as a validation/sensitivity check on the
placeholder AM peak-factor (1.35) rather than a direct replacement -- see
handoff.md section 7/9.2 for why AM-specific data could not be sampled."""

data = [
    # (band, km, total_s, delay_s)
    ("<5",    4.76, 1084, 23),
    ("<5",    1.75, 539, 0),
    ("<5",    0.51, 335, 0),
    ("<5",    2.25, 611, 0),
    ("<5",    0.26, 221, 0),
    ("5-10",  7.55, 1069, 0),
    ("5-10",  8.17, 1241, 0),
    ("5-10",  6.51, 1193, 244),
    ("5-10",  5.38, 1302, 0),
    ("5-10",  8.01, 1574, 17),
    ("10-15", 14.39, 1629, 225),
    ("10-15", 13.66, 2382, 860),
    ("10-15", 14.40, 2398, 541),
    ("10-15", 12.24, 1825, 370),
    ("10-15", 10.04, 1544, 26),
    (">15",   17.98, 1875, 26),
    (">15",   15.91, 2643, 373),
    (">15",   17.83, 2478, 732),
    (">15",   17.94, 2080, 0),
    (">15",   18.74, 2701, 632),
]

from collections import defaultdict
bands = defaultdict(list)
for band, km, total, delay in data:
    ratio = total / (total - delay) if delay else 1.0
    bands[band].append(ratio)

print(f"{'band':8s} {'n':3s} {'mean_ratio':10s} {'min':6s} {'max':6s}")
order = ["<5", "5-10", "10-15", ">15"]
for b in order:
    rs = bands[b]
    print(f"{b:8s} {len(rs):3d} {sum(rs)/len(rs):10.3f} {min(rs):6.3f} {max(rs):6.3f}")

overall = [r for b in order for r in bands[b]]
print(f"\noverall mean ratio: {sum(overall)/len(overall):.3f}  (n={len(overall)})")
print("placeholder assumption in run_onemap_routing.py: 1.35 (AM), 1.15 (PM)")
