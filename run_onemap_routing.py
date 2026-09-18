#!/usr/bin/env python3
"""
Buying Time in Singapore -- real routed travel times via the OneMap API.

Computes, for each home-estate / secondary-school pair:
  AM : departure time needed from home to ARRIVE at school by 07:30  (car + public transport)
  PM : arrival time back home when LEAVING school at 16:00           (car + public transport)

Usage
-----
    pip install requests
    python run_onemap_routing.py --token "<YOUR_ONEMAP_TOKEN>" --pairs buying_time_100_pairs.csv

Outputs  ->  onemap_results.csv   (one row per pair, real routed minutes)
             prints a summary block you can paste straight back into the chat

Notes
-----
* OneMap tokens last 3 days. Re-mint at https://www.onemap.gov.sg/apidocs/register
* Rate limit is 300 calls/min; this script self-throttles well under that.
* OneMap public transport routing is DEPART-AT only, so the 07:30 arrival is
  solved by iteration: guess a departure, route it, shift the departure by the
  error, re-route. Two iterations converge to within a couple of minutes.
* OneMap `drive` returns free-flow-ish times with no traffic model, so AM car
  times are inflated by PEAK_FACTOR to approximate 07:00-07:30 congestion.
  Set --peak-factor 1.0 to disable and report raw OneMap values.
"""

import argparse, csv, json, sys, time
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    sys.exit("Install requests first:  pip install requests")

BASE = "https://www.onemap.gov.sg/api/public/routingsvc/route"
SCHOOL_DAY = datetime(2026, 9, 18)          # a Friday in term time
ARRIVE_BY   = timedelta(hours=7, minutes=30)
DEPART_PM   = timedelta(hours=16)
PARK_WALK   = 5.0                            # min: walk to car, park, walk into school


def call(session, token, start, end, route_type, when=None, tries=3):
    """One OneMap routing call. Returns parsed JSON or None."""
    params = {
        "start": f"{start[0]:.6f},{start[1]:.6f}",
        "end":   f"{end[0]:.6f},{end[1]:.6f}",
        "routeType": route_type,
    }
    if route_type == "pt":
        params.update({
            "date": when.strftime("%m-%d-%Y"),
            "time": when.strftime("%H:%M:%S"),
            "mode": "TRANSIT",
            "maxWalkDistance": "1200",
            "numItineraries": "1",
        })
    for attempt in range(tries):
        try:
            r = session.get(BASE, params=params,
                            headers={"Authorization": token}, timeout=30)
            if r.status_code == 429:
                time.sleep(2 + attempt * 3); continue
            if r.status_code == 401:
                sys.exit("Token rejected (401). Mint a fresh one -- they expire after 3 days.")
            r.raise_for_status()
            return r.json()
        except Exception:
            if attempt == tries - 1:
                return None
            time.sleep(1.5 * (attempt + 1))
    return None


def drive_minutes(js):
    if not js:
        return None
    rs = js.get("route_summary") or {}
    t = rs.get("total_time")
    return round(t / 60.0, 1) if t else None


def pt_minutes(js):
    """Returns (total_min, walk_min, wait_min, transfers) or Nones."""
    if not js:
        return None, None, None, None
    its = (js.get("plan") or {}).get("itineraries") or []
    if not its:
        return None, None, None, None
    it = its[0]
    return (round(it.get("duration", 0) / 60.0, 1),
            round(it.get("walkTime", 0) / 60.0, 1),
            round(it.get("waitingTime", 0) / 60.0, 1),
            it.get("transfers"))


def pt_arrive_by(session, token, start, end, target_dt, seed_minutes=55.0):
    """Iterate a depart-at query until the arrival lands on target_dt."""
    guess = seed_minutes
    best = (None, None, None, None, None)
    for _ in range(3):
        depart = target_dt - timedelta(minutes=guess)
        js = call(session, token, start, end, "pt", when=depart)
        total, walk, wait, tr = pt_minutes(js)
        if total is None:
            return best
        best = (total, walk, wait, tr, depart)
        err = total - guess
        if abs(err) <= 2.0:
            break
        guess = total
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", required=True)
    ap.add_argument("--pairs", default="buying_time_100_pairs.csv")
    ap.add_argument("--out",   default="onemap_results.csv")
    ap.add_argument("--peak-factor", type=float, default=1.35,
                    help="multiplier on OneMap drive time for the AM peak (1.0 = raw)")
    ap.add_argument("--pm-factor", type=float, default=1.15)
    ap.add_argument("--limit", type=int, default=0, help="only process first N pairs (testing)")
    ap.add_argument("--estates", default="hdb_estates_142.csv")
    ap.add_argument("--schools", default="secondary_schools_146.csv")
    a = ap.parse_args()

    rows = list(csv.DictReader(open(a.pairs, newline="", encoding="utf-8")))
    if a.limit:
        rows = rows[: a.limit]

    # the pairs CSV carries names but not coords -- rejoin from the estate/school files
    est = {r["estate"]: (float(r["lat"]), float(r["lon"]))
           for r in csv.DictReader(open(a.estates, newline="", encoding="utf-8"))}
    sch = {r["school"]: (float(r["lat"]), float(r["lon"]))
           for r in csv.DictReader(open(a.schools, newline="", encoding="utf-8"))}

    arrive_dt = SCHOOL_DAY + ARRIVE_BY
    depart_dt = SCHOOL_DAY + DEPART_PM
    s = requests.Session()
    out, failures = [], 0

    for i, r in enumerate(rows, 1):
        home, school = est.get(r["estate"]), sch.get(r["school"])
        if not home or not school:
            failures += 1
            continue

        car_raw_am = drive_minutes(call(s, token := a.token, home, school, "drive"))
        car_raw_pm = drive_minutes(call(s, token, school, home, "drive"))
        pt_am, w_am, q_am, tr_am, dep_am = pt_arrive_by(
            s, token, home, school, arrive_dt, seed_minutes=float(r.get("pt_am_min") or 55))
        js_pm = call(s, token, school, home, "pt", when=depart_dt)
        pt_pm, w_pm, q_pm, tr_pm = pt_minutes(js_pm)

        if None in (car_raw_am, car_raw_pm, pt_am, pt_pm):
            failures += 1
            print(f"  [{i:3d}] FAILED  {r['estate']} -> {r['school']}")
            continue

        car_am = round(car_raw_am * a.peak_factor + PARK_WALK, 1)
        car_pm = round(car_raw_pm * a.pm_factor + PARK_WALK, 1)

        def hhmm(td):
            m = int(round(td)); return f"{m // 60:02d}:{m % 60:02d}"

        out.append({
            "id": r["id"], "estate": r["estate"], "town": r.get("town", ""),
            "school": r["school"], "km": r.get("km", ""),
            "car_am_min": car_am, "pt_am_min": pt_am, "adv_am_min": round(pt_am - car_am, 1),
            "car_pm_min": car_pm, "pt_pm_min": pt_pm, "adv_pm_min": round(pt_pm - car_pm, 1),
            "adv_day_min": round((pt_am - car_am) + (pt_pm - car_pm), 1),
            "depart_car": hhmm(7 * 60 + 30 - car_am),
            "depart_pt":  hhmm(7 * 60 + 30 - pt_am),
            "arrive_car": hhmm(16 * 60 + car_pm),
            "arrive_pt":  hhmm(16 * 60 + pt_pm),
            "pt_walk_min": w_am, "pt_wait_min": q_am, "pt_transfers": tr_am,
            "car_raw_am": car_raw_am,
        })
        print(f"  [{i:3d}] {r['estate'][:30]:<30} -> {r['school'][:26]:<26} "
              f"car {car_am:5.1f}  pt {pt_am:5.1f}  adv +{pt_am - car_am:5.1f}")
        time.sleep(0.25)          # ~4 calls/s, comfortably under 300/min

    if not out:
        sys.exit("No successful routes -- check the token and the CSV paths.")

    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)

    mean = lambda k: sum(float(o[k]) for o in out) / len(out)
    med  = lambda k: sorted(float(o[k]) for o in out)[len(out) // 2]
    adv_day = mean("adv_day_min")
    print("\n" + "=" * 62)
    print(f"  pairs routed          {len(out)}   (failed: {failures})")
    print(f"  car  AM  mean         {mean('car_am_min'):.1f} min")
    print(f"  PT   AM  mean         {mean('pt_am_min'):.1f} min")
    print(f"  ADVANTAGE AM  mean    {mean('adv_am_min'):.1f} min   median {med('adv_am_min'):.1f}")
    print(f"  ADVANTAGE PM  mean    {mean('adv_pm_min'):.1f} min")
    print(f"  ADVANTAGE / day       {adv_day:.1f} min")
    print(f"  per school year       {adv_day * 190 / 60:.0f} hours")
    print(f"  over 4 years          {adv_day * 190 * 4 / 60:.0f} hours "
          f"= {adv_day * 190 * 4 / 60 / 24:.0f} days")
    print(f"  PT / car ratio        {mean('pt_am_min') / mean('car_am_min'):.2f}x")
    print("=" * 62)
    print(f"\nWrote {a.out} -- paste that file back into the chat to rebuild the dashboard.")


if __name__ == "__main__":
    main()
