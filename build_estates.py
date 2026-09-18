#!/usr/bin/env python3
"""Rebuild HDB estates from the authoritative HDB Property Information join,
population-weighted by total_dwelling_units. Replaces the old block-count-biased
clustering (handoff.md section 5.1/5.2/8-item-1)."""
import csv
from math import cos, radians
import numpy as np
from sklearn.cluster import KMeans

rows = list(csv.DictReader(open("hdb_blocks_joined.csv", encoding="utf-8")))
for r in rows:
    r["lat"] = float(r["lat"])
    r["lon"] = float(r["lon"])
    r["units"] = max(1, int(r["total_dwelling_units"] or 0))

towns = sorted(set(r["town"] for r in rows))
estates = []

for town in towns:
    trows = [r for r in rows if r["town"] == town]
    lat = np.array([r["lat"] for r in trows])
    lon = np.array([r["lon"] for r in trows])
    units = np.array([r["units"] for r in trows], dtype=float)

    latkm = (lat.max() - lat.min()) * 111.32
    lonkm = (lon.max() - lon.min()) * 111.32 * cos(radians(1.35))
    area = max(latkm * lonkm, 0.6)
    k = int(max(1, min(10, round(area / 1.6))))

    X = np.column_stack([lat, lon])
    if k == 1 or len(trows) < k:
        labels = np.zeros(len(trows), dtype=int)
        k = 1
    else:
        km = KMeans(n_clusters=k, n_init=10, random_state=42)
        labels = km.fit_predict(X, sample_weight=units)

    for c in range(k):
        mask = labels == c
        if not mask.any():
            continue
        w = units[mask]
        clat = float(np.average(lat[mask], weights=w))
        clon = float(np.average(lon[mask], weights=w))
        member_streets = [trows[i]["street"] for i in range(len(trows)) if mask[i]]
        top_street = max(set(member_streets), key=member_streets.count)
        estates.append({
            "estate": f"{town.title()} – {top_street.title()}",
            "town": town.title(),
            "lat": round(clat, 6),
            "lon": round(clon, 6),
            "hdb_blocks": int(mask.sum()),
            "dwelling_units": int(w.sum()),
        })

# de-dup identical estate names within a town by appending a cardinal-ish suffix
from collections import Counter
name_counts = Counter(e["estate"] for e in estates)
seen = Counter()
for e in estates:
    if name_counts[e["estate"]] > 1:
        seen[e["estate"]] += 1
        e["estate"] = f"{e['estate']} ({seen[e['estate']]})"

with open("hdb_estates_weighted.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["estate", "town", "lat", "lon", "hdb_blocks", "dwelling_units"])
    w.writeheader()
    w.writerows(estates)

print(f"{len(estates)} estates across {len(towns)} towns")
print(f"total dwelling units captured: {sum(e['dwelling_units'] for e in estates):,}")
