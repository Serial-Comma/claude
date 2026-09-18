#!/usr/bin/env python3
"""Compute all dashboard stats from routed OneMap results."""
import csv, json, sys

def load(path):
    return list(csv.DictReader(open(path, newline="", encoding="utf-8")))

def band(km):
    if km < 5: return "<5"
    if km < 10: return "5-10"
    if km < 15: return "10-15"
    return ">15"

def stats(rows):
    n = len(rows)
    def f(k): return [float(r[k]) for r in rows]
    car_am, pt_am, adv_am = f("car_am_min"), f("pt_am_min"), f("adv_am_min")
    car_pm, pt_pm, adv_pm = f("car_pm_min"), f("pt_pm_min"), f("adv_pm_min")
    adv_day = f("adv_day_min")
    km = f("km")
    mean = lambda xs: sum(xs)/len(xs)
    med = lambda xs: sorted(xs)[len(xs)//2]
    def pctile(xs, p):
        s = sorted(xs); k = (len(s)-1)*p
        f_, c_ = int(k), min(int(k)+1, len(s)-1)
        return s[f_] + (s[c_]-s[f_])*(k-f_)

    bands = {}
    for b in ["<5", "5-10", "10-15", ">15"]:
        br = [r for r in rows if band(float(r["km"])) == b]
        if not br: continue
        bands[b] = {
            "n": len(br),
            "car": round(mean([float(r["car_am_min"]) for r in br]), 1),
            "pt": round(mean([float(r["pt_am_min"]) for r in br]), 1),
            "adv": round(mean([float(r["adv_am_min"]) for r in br]), 1),
        }

    adv_day_mean = mean(adv_day)
    return {
        "n": n,
        "car_am_mean": round(mean(car_am), 1),
        "pt_am_mean": round(mean(pt_am), 1),
        "adv_am_mean": round(mean(adv_am), 1),
        "adv_am_median": round(med(adv_am), 1),
        "adv_am_p10": round(pctile(adv_am, 0.10), 1),
        "adv_am_p90": round(pctile(adv_am, 0.90), 1),
        "adv_pm_mean": round(mean(adv_pm), 1),
        "car_pm_mean": round(mean(car_pm), 1),
        "pt_pm_mean": round(mean(pt_pm), 1),
        "adv_day_mean": round(adv_day_mean, 1),
        "per_year_hours": round(adv_day_mean * 190 / 60, 0),
        "per_4yr_hours": round(adv_day_mean * 190 * 4 / 60, 0),
        "per_4yr_days": round(adv_day_mean * 190 * 4 / 60 / 24, 1),
        "pt_car_ratio": round(mean(pt_am) / mean(car_am), 2),
        "mean_km": round(mean(km), 2),
        "median_km": round(med(km), 2),
        "bands": bands,
    }

v1 = load("onemap_results_v1_original_pairs.csv")
out = {"v1": stats(v1)}

try:
    v2 = load("onemap_results_v2.csv")
    if v2:
        out["v2"] = stats(v2)
except FileNotFoundError:
    pass

with open("dashboard_stats.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)

print(json.dumps(out, indent=2))
