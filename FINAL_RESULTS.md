# Buying Time in Singapore — Final Results

Generated 2026-09-17, Claude Code session. Full raw data: `final_results_raw.json` (191 trips + methodology + calibration). This file is the human-readable companion — measured numbers first, extrapolations clearly separated after.

---

## 1. MEASURED (directly computed from routed data — no guesswork)

**191 real OneMap-routed home→school trips, two independent random samples (seed=2026), AM car time corrected with the measured ×1.175 Google Maps peak-traffic factor.**

| Metric | Value |
|---|---|
| AM advantage, mean | **28.9 min** |
| AM advantage, median | 26.1 min |
| AM advantage, p10–p90 | 9.2 – 55.1 min |
| PM advantage, mean | 26.6 min |
| Advantage per school day | **55.5 min** |
| Per school year (190 days) | **176 hours** |
| Over a 4-year secondary career | **703 hours = 29.3 days (24h) = 43.9 days (16h waking)** |
| Car mean AM time | 34.3 min |
| PT mean AM time | 63.2 min |
| PT/car ratio | 1.84× |
| Mean home–school distance (random pairing) | 11.4 km |

**By distance band:**

| Band | n | Car (min) | PT (min) | Advantage (min) |
|---|---|---|---|---|
| <5 km | 24 | 16.5 | 33.1 | 16.6 |
| 5–10 km | 57 | 27.0 | 47.0 | 20.0 |
| 10–15 km | 56 | 37.6 | 73.5 | 35.9 |
| >15 km | 54 | 46.5 | 83.0 | 36.5 |

**Traffic calibration (measured, not assumed):**
- AM car-time correction factor: **×1.175**, measured against Google Maps "Arrive by 07:30, Fri 18 Sep 2026" predictive traffic vs. OneMap free-flow, n=10 routes across all 4 distance bands. Replaces an earlier placeholder of ×1.35.
- Secondary check: TomTom live traffic, n=20, Thu 17 Sep ~18:45 SGT (evening, not the target window) — shown in the dashboard for transparency; disagrees with Google on which distance band is worst-congested, a discrepancy worth naming if asked in the viva.
- PM car-time correction remains an **unverified placeholder (×1.15)** — only the AM window was measured this session.

**Sample replication** (evidence the result isn't an artifact of one estate/school list):

| | Sample A (original 142-estate/146-school lists) | Sample B (authoritative 186-estate/133-school lists) |
|---|---|---|
| n routed | 93/100 | 98/100 |
| AM advantage mean | 29.6 min | 28.2 min |

---

## 2. EXTRAPOLATIONS & BEST GUESSTIMATES (labeled — not measured, use with the caveats attached)

These translate the measured numbers into more intuitive or rhetorically usable framings. Each carries a confidence note. None of these should be presented as directly measured facts in the viva — they're illustrative arithmetic on top of the measured result.

| Framing | Guesstimate | Confidence / caveat |
|---|---|---|
| "A month of the child's life" | 703 hours ≈ **29.3 full days**, or **43.9 days of waking (16h) time**, over 4 years | High — pure unit conversion of the measured number, no external assumption |
| Morning sleep/prep time alone | AM-only advantage compounds to **366 hours (≈15.3 days) over 4 years** just from the morning leg | High — same, isolates AM from the pooled AM+PM figure |
| "Price per hour of time bought" | COE Category A's record S$133,009 ÷ 703 hours = **≈S$189 per hour of morning-and-afternoon time bought back**, if the entire COE premium were attributed to this one benefit | **Low-to-illustrative only.** The COE buys the whole car and every use of it (work commute, groceries, leisure, the other three domains in the thesis), not just this one benefit stream — this number is a rhetorical device ("here's one lens on the price of time"), not a real unit cost. State that caveat in the same breath if used. |
| Dollar-equivalent of time saved | At Singapore's approx. median gross monthly income (~S$5,500, **not independently re-verified this session**) ⇒ ~S$31/hour ⇒ **≈S$5,500/year** of nominal time value | **Use with real caution.** This is close to a literal "time = income" framing — exactly the objection Atkinson/Bourdieu pre-empt in the thesis (converting economic capital into cultural capital *presupposes* time, it isn't reducible to it). If used at all, frame it as "here's what the objection would even look like quantified" rather than as supporting evidence. |
| Population-scale (Singapore-wide) | Not computed. Would require (a) an authoritative current secondary-enrolment figure and (b) car-ownership-rate-by-income-quintile data to weight by, neither pulled this session — a population total built from the household car-ownership split already in §12 of `handoff.md` (36.3% overall vs. 17.0% lowest quintile) would be more defensible than a flat population multiply. Flagging as a gap rather than guessing a number. |

---

## 3. What changed since the last handoff version

- AM car times were re-corrected using a **measured** traffic factor (×1.175, from real Google Maps AM-peak data) instead of the earlier placeholder (×1.35). This *increased* the reported advantage (24.5 → 28.9 min pooled AM mean), because real AM congestion on these routes was lighter than the placeholder assumed.
- All figures in this file reflect that correction. `onemap_results_v1_original_pairs.csv` / `onemap_results_v2.csv` carry both values — the corrected `car_am_min` and, for audit, the original placeholder-based figure in `car_am_min_old135`.
