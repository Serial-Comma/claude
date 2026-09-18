#!/usr/bin/env python3
"""Draw 100 random (estate, school) pairs from the authoritative data sources,
same method as the original handoff pipeline: uniform draw, seed=2026."""
import csv, random
from math import radians, sin, cos, asin, sqrt

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 2 * 6371 * asin(sqrt(a))

estates = list(csv.DictReader(open("hdb_estates_weighted.csv", encoding="utf-8")))
schools = list(csv.DictReader(open("secondary_schools_moe.csv", encoding="utf-8")))

random.seed(2026)
pairs = [(random.choice(estates), random.choice(schools)) for _ in range(100)]

out = []
for i, (e, s) in enumerate(pairs, 1):
    km = haversine(float(e["lat"]), float(e["lon"]), float(s["lat"]), float(s["lon"]))
    out.append({
        "id": i, "estate": e["estate"], "town": e["town"], "school": s["school"],
        "km": round(km, 2),
    })

with open("buying_time_100_pairs_v2.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["id", "estate", "town", "school", "km"])
    w.writeheader(); w.writerows(out)

dists = sorted(o["km"] for o in out)
print(f"{len(out)} pairs drawn")
print(f"mean distance: {sum(dists)/len(dists):.2f} km, median: {dists[len(dists)//2]:.2f} km")
