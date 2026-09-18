#!/usr/bin/env python3
"""Geocode the official MOE secondary school list via OneMap Search API."""
import argparse, csv, sys, time
import requests

SEARCH = "https://www.onemap.gov.sg/api/common/elastic/search"

def geocode(session, token, postal):
    params = {"searchVal": postal, "returnGeom": "Y", "getAddrDetails": "Y", "pageNum": 1}
    for attempt in range(3):
        try:
            r = session.get(SEARCH, params=params, headers={"Authorization": token}, timeout=15)
            r.raise_for_status()
            js = r.json()
            results = js.get("results") or []
            if results:
                res = results[0]
                return float(res["LATITUDE"]), float(res["LONGITUDE"]), res.get("ADDRESS", "")
            return None
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", required=True)
    ap.add_argument("--in-csv", default="moe_schools_raw.csv")
    ap.add_argument("--out", default="secondary_schools_moe.csv")
    a = ap.parse_args()

    rows = list(csv.DictReader(open(a.in_csv, newline="", encoding="utf-8")))
    sec = [r for r in rows if r["mainlevel_code"] in ("SECONDARY (S1-S5)", "SECONDARY (S1-S4)")]
    print(f"{len(sec)} official secondary schools to geocode")

    s = requests.Session()
    out, failed = [], []
    for i, r in enumerate(sec, 1):
        postal = r["postal_code"].strip()
        g = geocode(s, a.token, postal)
        if not g:
            failed.append(r["school_name"])
            print(f"  [{i:3d}] FAILED  {r['school_name']} ({postal})")
            time.sleep(0.2)
            continue
        lat, lon, addr = g
        out.append({
            "school": r["school_name"].title(),
            "postal": postal,
            "lat": lat,
            "lon": lon,
            "address": addr,
        })
        print(f"  [{i:3d}] {r['school_name'][:40]:<40} {lat:.5f},{lon:.5f}")
        time.sleep(0.2)

    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["school", "postal", "lat", "lon", "address"])
        w.writeheader(); w.writerows(out)

    print(f"\nGeocoded {len(out)}/{len(sec)}. Failed: {failed}")
    print(f"Wrote {a.out}")

if __name__ == "__main__":
    main()
