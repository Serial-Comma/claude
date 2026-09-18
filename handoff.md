# handoff.md — "Buying Time in Singapore" quantitative exhibit

**Status:** RESOLVED by Claude Code, 17 September 2026. Real OneMap-routed data (191 trips, two independent samples) replaces the modelled numbers. Dashboard republished: https://claude.ai/artifact/756yrSTy9HAUQKAgPXCfQe
**Deadline:** Viva Voce, Friday 18 September 2026, 14:00 SGT.
**Written:** 17 September 2026 (original handoff below, kept for methodology/viva-prep reference).

## Update log (Claude Code, 17 Sep 2026)

Network egress was NOT blocked in this environment (verified `onemap.gov.sg`, `data.gov.sg`, general internet all reachable) — the sandbox restriction in §7 below did not apply here. All four priority items in §10 were completed:

1. **Real routing (§10.1)** — ran `run_onemap_routing.py` on the original 100 pairs: **93/100 routed, AM advantage 25.3 min** (model predicted 22–30 min ✅). Output: `onemap_results_v1_original_pairs.csv`.
2. **Traffic correction check (§10.2)** — used TomTom (authorized by user) to sample live traffic on 20 calibration routes across all 4 distance bands. Congestion scales with distance (~0% under 5 km, up to ~26% beyond 10 km on expressway bottlenecks), but this was an evening snapshot (18:43 SGT), not the true 07:00–07:30 AM window — TomTom's historical-traffic mode returned zero delay for future AM departures on this account, so true AM data couldn't be sampled. Kept the existing ×1.35/×1.15 placeholder as the conservative choice; documented the live-traffic finding as a validation note in the dashboard rather than replacing the factor with off-peak data.
3. **School list (§10.3)** — pulled the official MOE "General Information of Schools" dataset from `data.gov.sg` (dataset `d_688b934f82c1059ed0a6993d2a829089`), filtered to `SECONDARY (S1-S5)` + `SECONDARY (S1-S4)` = **133 schools**, geocoded via OneMap Search. Output: `secondary_schools_moe.csv`.
4. **HDB estate weighting (§10.4)** — pulled **HDB Property Information** from `data.gov.sg` (dataset `d_17f5382f26140b1fdae0ba2ef6239d2f`, 13,357 blocks with `total_dwelling_units`), joined to coordinates via `buildings.json` (97.3% match rate after expanding street abbreviations), rebuilt **186 dwelling-unit-weighted estates** across 27 towns. This fixes the severe Bedok (153→631 blocks) and Ang Mo Kio (81→451 blocks) undercount flagged in §8 item 1. **Note:** the `bldg_contract_town` codes `TAP`/`TP` are swapped from the intuitive reading — `TAP` = Tampines, `TP` = Toa Payoh, confirmed against street names. Output: `hdb_estates_weighted.csv`, `hdb_blocks_joined.csv`.

A **second independent 100-pair sample** (seed=2026, same uniform-draw method) was redrawn from the authoritative estate/school lists and also routed: **98/100 routed, AM advantage 23.8 min** — closely replicating Sample A. Output: `onemap_results_v2.csv`, pairs in `buying_time_100_pairs_v2.csv`.

**Pooled headline (n=191, both samples):** AM advantage mean **24.5 min** (median 21.5), **51.2 min/school day**, **162 hours/year**, **648 hours ≈ 27.0 days over a 4-year secondary career**. Distance-band compounding confirmed: <5km +14.9min → >15km +30.3min advantage.

## Update log 2 — real AM-peak traffic factor (Claude Code, 17 Sep 2026, later same session)

User supplied a Google Maps API key. First two keys were blocked (no Directions/Routes API enabled, then billing not enabled on the Cloud project) — server-side API was a dead end within the time available. **Worked instead: driving the Google Maps *website* via the Claude-in-Chrome browser extension**, using its "Arrive by" feature to query **10 routes** (spanning all 4 distance bands) for "Arrive by 07:30 AM, Fri 18 Sep 2026" — the actual real target arrival time, not a proxy. This is Google's predictive/historical traffic model for that specific real future time slot, genuinely different from TomTom's `live` mode (real-time only) and `historical` mode (returned zero delay for future dates on the TomTom account — see Update log 1).

Compared each route's Google "Best" AM-peak duration against OneMap's free-flow drive time for the same route:

| Band | n | mean ratio (Google AM / OneMap free-flow) |
|---|---|---|
| <5 km | 2 | 1.263 |
| 5–10 km | 3 | 1.328 |
| 10–15 km | 3 | 1.030 |
| >15 km | 2 | 1.076 |
| **Pooled** | **10** | **1.175** |

This **replaced** the placeholder ×1.35 AM factor (pooled ×1.175 applied uniformly — band-level split not used, sample too thin at n=2–3/band to trust the non-monotonic pattern for a per-band factor, though it's shown in the dashboard for transparency). Recomputed `car_am_min`, `adv_am_min`, `adv_day_min` in both result CSVs.

**Effect:** because the real AM factor (1.175) is *lower* than the placeholder (1.35), car times got *faster*, not slower, so the advantage **increased**:
- Sample A: 25.3 → **29.6 min** AM advantage
- Sample B: 23.8 → **28.2 min**
- **New pooled headline: 28.9 min AM advantage (median 26.1), 55.5 min/day, 176 hrs/year, 703 hrs ≈ 29.3 days over 4 years** — now even closer to the original pre-registered model's 26.2 min / 30 days.

PM leg still uses the unmeasured ×1.15 placeholder — only the AM window was tested (that's what was asked for). Dashboard traffic-note section rewritten to lead with this Google Maps AM-peak measurement and demote the TomTom evening snapshot to a secondary/contradicting check (the two sources disagree on *which* distance band is most congested — worth pre-empting in the viva if asked which is more reliable: Google's, because it targets the real 07:00–07:30 window).

Dashboard republished (Version 2, same URL). `onemap_results_v1_original_pairs.csv` and `onemap_results_v2.csv` overwritten in place with corrected AM columns; original ×1.35 values preserved in a new `car_am_min_old135` column for audit.

Dashboard rebuilt from scratch (original artifact's source wasn't available locally) at `buying_time_dashboard.html`, republished to the same handoff-era styling philosophy (self-contained, theme-aware, zero external deps beyond Google Fonts + Chart.js from the CSP-allowed CDN). New file inventory in §11 below is superseded — see the file list at the end of this update log.

**Files added this session** (all in the project root):
`onemap_results_v1_original_pairs.csv`, `onemap_results_v2.csv`, `buying_time_100_pairs_v2.csv`, `hdb_estates_weighted.csv`, `hdb_blocks_joined.csv`, `hdb_property_info.csv`, `secondary_schools_moe.csv`, `moe_schools_raw.csv`, `buildings.json`, `dashboard_data.json`, `buying_time_dashboard.html`, plus helper scripts `build_estates.py`, `build_pairs_v2.py`, `geocode_schools.py`, `compute_stats.py`, `tomtom_calibration.py`.

**Still open / lowest priority (§10.6 optional extensions):** sensitivity analysis on PT_DETOUR/transfer penalty, nearest-school counterfactual, other domains (tuition, healthcare). Not attempted — pooled n=191 real-routed result is solid enough for the viva as-is, and these were explicitly marked optional/time-permitting.

---

---

## 1. Purpose and academic context

This is coursework, not a product. The quantitative work exists to supply **one empirical exhibit** inside a 12-minute oral presentation.

| Item | Value |
|---|---|
| Module | *Understanding the Social World: Singapore and Beyond* (USW), NUS College |
| Assessment | Viva Voce, 25% of grade |
| Format | 12 min presentation + 8 min professor Q&A (15–20 min total) |
| Requirement | Must analyse **a popular-press artifact** (article, editorial, or TV programme) *using class readings as a lens* |
| Scope rule | Topic must be *in* Singapore, *of* Singapore, or *elsewhere related to* Singapore |

### Thesis
**"Buying Time in Singapore":** money buys **time**, time buys **advantage**, accumulated advantage constitutes and reproduces **class**. The paradigm case is private car ownership, made exclusionary by the Certificate of Entitlement (COE). Four extension domains: education (tuition), domestic labour (helpers), healthcare (queue-jumping), social capital (ferrying/favour exchange).

### Theoretical spine
Bourdieu, *The Forms of Capital* (1986): the conversion of economic capital into cultural capital *presupposes an expenditure of time made possible by economic capital*. This is the rebuttal to the single most dangerous objection — "time is just income re-described."

### Readings available (Weeks 1–5 only)
Cialdini (normative messages); Berger (*Invitation to Sociology* ch.4); Feng/Wang/Poston (one-child policy); Heng & Devan (State Fatherhood); Poon (Pick and Mix); Moore (Multiracialism & Meritocracy); Lim/Chen/Hiramoto (Mandarin ideologies); Orsi (lived religion); Sinha (sacred spaces); Thio (principled pluralism); **Atkinson, *Class: Key Concepts* ch.2 Exploitation, ch.3 Life Chances**; **Debs & Cheung, structure-reinforced privilege (primary school choice)**; **Teo/Nur Diyanah/Vasu/Prakash, RSIS Singaporean Youth and Socio-economic Mobility**.

The last three carry the argument. Debs & Cheung is the direct bridge to this school-commute analysis.

---

## 2. What the quantitative exhibit measures

> How much time does a family car buy back for a secondary-school child, per day, per year, and across a four-year school career — relative to public transport?

Operationalised as: for 100 randomly drawn (HDB estate → public secondary school) pairs, compute door-to-door travel time by **car** and by **public transport**, in both directions:

- **AM leg:** must **arrive** at school by **07:30**. Output = required departure time from home.
- **PM leg:** **departs** school at **16:00**. Output = arrival time back home.

Derived metrics: per-trip advantage, per-day advantage, wake-up-time gap, cumulative hours over 190 school days/year × 4 years.

---

## 3. Architecture

```
                    raw source (GitHub mirror of OneMap postal dump)
                                    │
                    buildings.json  │  141,726 geocoded SG addresses
                                    ▼
             ┌──────────────────────┴──────────────────────┐
             │                                             │
      HDB block filter                             school name filter
      (BUILDING prefix + road rules)               (include/exclude patterns)
             │  7,200 blocks                              │  146 schools
             ▼                                             │
      per-town k-means clustering                          │
             │  142 estate centroids                       │
             └──────────────────────┬──────────────────────┘
                                    ▼
                    uniform random pairing (seed=2026)
                                    │  100 pairs
                                    ▼
             ┌──────────────────────┴──────────────────────┐
             │                                             │
    [DONE] analytic travel-time model          [BLOCKED] OneMap routed times
             │                                             │
             └──────────────────────┬──────────────────────┘
                                    ▼
                    stats + SVG charts + HTML dashboard
```

**Design principle throughout:** every choice that could bias the result was resolved *against* the thesis, so the reported advantage is a floor, not a ceiling.

---

## 4. Data sources

### 4.1 Primary — geocoded address dump
- **URL:** `https://raw.githubusercontent.com/xkjyeah/singapore-postal-codes/master/buildings.json`
- **Size:** 57,232,418 bytes · **Records:** 141,726
- **Provenance:** scraped from OneMap (SLA). Open Data Licence. Vintage roughly 2017–2021.
- **Why this and not data.gov.sg:** `data.gov.sg` is blocked by the sandbox egress allowlist (see §7). GitHub raw is reachable.

Record schema:
```json
{
  "ADDRESS":    "1 STRAITS BOULEVARD SINGAPORE CHINESE CULTURAL CENTRE SINGAPORE 018906",
  "BLK_NO":     "1",
  "BUILDING":   "SINGAPORE CHINESE CULTURAL CENTRE",
  "LATITUDE":   "1.2758046353113",
  "LONGITUDE":  "103.849615008325",
  "LONGTITUDE": "103.849615008325",
  "POSTAL":     "018906",
  "ROAD_NAME":  "STRAITS BOULEVARD",
  "SEARCHVAL":  "SINGAPORE CHINESE CULTURAL CENTRE",
  "X":          "29813.6634912575",
  "Y":          "28697.5207557455"
}
```
`X`/`Y` are SVY21 projected metres. `LONGTITUDE` is a typo'd duplicate present in the source — ignore it.

### 4.2 Calibration benchmarks (from literature, not fetched)
- LTA Household Travel Survey 2024: mean/median weekday travel **30–35 min to school**, 40–45 min to work; *no significant trend by housing type*.
- LTMP 2040 target: "45-Minute City, 20-Minute Towns." As of 2023 only **67%** could reach work within 45 min.
- Average SG public-transport commute ≈ 84 min/weekday (round trip).
- 2026 town survey: longest commutes from Sembawang, Bukit Panjang, Punggol, Sengkang; shortest from Tanglin (~25 min), Bukit Timah, Novena.

---

## 5. Technical decisions and rationale

### 5.1 Identifying HDB blocks — **decided: two-rule filter**

The dump has no HDB flag. Three approaches were tried:

| Approach | Result | Verdict |
|---|---|---|
| `BUILDING` starts with `HDB-` | 5,201 blocks, town label embedded (`HDB-ANG MO KIO`) | Clean but **misses new towns** — Sengkang 28, Punggol 65, because BTO blocks carry project names (`COMPASSVALE HAVEN`) |
| Absorb any block within 1.2 km of an `HDB-` seed | 78,745 blocks | **Rejected** — pulled in private condos and landed housing (Bukit Timah 3,808; Central Area 4,258) |
| `HDB-` prefix **+** curated new-town road-name rules | **7,200 blocks, all 25 towns** | **Adopted** |

Adopted rule:
```python
def is_blk(r):  # numeric block number, optional letter suffix
    return re.match(r'^\d{1,4}[A-Z]?$', (r['BLK_NO'] or '').strip()) is not None

# rule 1: explicit HDB tag, town label = BUILDING[4:]
if r['BUILDING'].startswith('HDB-') and is_blk(r): keep(town=r['BUILDING'][4:])

# rule 2: new-town road families (streets that are overwhelmingly HDB)
NEWTOWN = {
 'ANCHORVALE':'SENGKANG','COMPASSVALE':'SENGKANG','RIVERVALE':'SENGKANG',
 'FERNVALE':'SENGKANG','SENGKANG':'SENGKANG',
 'PUNGGOL':'PUNGGOL','EDGEDALE':'PUNGGOL','EDGEFIELD':'PUNGGOL','SUMANG':'PUNGGOL',
 'NORTHSHORE':'PUNGGOL','MATILDA':'PUNGGOL','WATERWAY':'PUNGGOL',
 'TENGAH':'TENGAH','PLANTATION':'TENGAH','CANBERRA':'SEMBAWANG'}
# excluded from rule 2 if BUILDING matches CONDO or NONRES keyword lists
CONDO  = ['RESIDENCE','CONDO','SUITES','EXECUTIVE','PARC ','THE ','RIVERTREES',
          'HIGH PARK','WATERWOODS','TREASURE','JEWEL','ECOPOLITAN','WATERBANK','PRIVE']
NONRES = ['CAR PARK','SHELTER','MARKET','HAWKER','COMMUNITY','SCHOOL','CHURCH','MOSQUE',
          'TEMPLE','POLYCLINIC','SUBSTATION','MRT','LRT','STATION','CLUB','SPORT',
          'STADIUM','LIBRARY','POLICE','FIRE','CHILDCARE','KINDERGARTEN','MALL',
          'PLAZA','POINT','WATERPOINT']
```
Legacy micro-town labels were merged into parent towns (`SERANGOON NORTH ESTATE`→`SERANGOON`, `GHIM MOH`→`QUEENSTOWN`, `POTONG PASIR`→`TOA PAYOH`, etc.). `BUKIT TIMAH` dropped entirely — not an HDB town.

Final town distribution (blocks): Sengkang 1001, Punggol 815, Woodlands 556, Jurong West 504, Tampines 456, Hougang 453, Choa Chu Kang 426, Pasir Ris 417, Yishun 252, Bukit Batok 245, Sembawang 242, Bukit Panjang 233, Serangoon 190, Bukit Merah 164, Bedok 153, Jurong East 148, Bishan 143, Tengah 134, Clementi 126, Geylang 119, Toa Payoh 113, Kallang/Whampoa 103, Queenstown 86, Ang Mo Kio 81, Central Area 40.

> **Known bias:** these counts do **not** reflect true HDB stock (Bedok and Ang Mo Kio are badly under-counted). This is why sampling is **uniform over estates**, never block-weighted — see §5.3.

### 5.2 Estate construction — **decided: spatial k-means, area-normalised**

"Group collections of blocks together" → cluster blocks into estate-sized units. Cluster count is driven by **land area, not block count**, so estate density is uniform in space and immune to the counting bias above.

```python
latkm = (lat.max()-lat.min()) * 111.32
lonkm = (lon.max()-lon.min()) * 111.32 * cos(radians(1.35))
area  = max(latkm*lonkm, 0.6)
k     = int(max(1, min(10, round(area/1.6))))     # ~1 estate per 1.6 km²
KMeans(n_clusters=k, n_init=10, random_state=42)
```
Estate name = `"{Town} – {most common ROAD_NAME in cluster}"`. Centroid = mean lat/lon of member blocks (a rough proxy for population weighting within the estate).

Output: 144 clusters → **142 estates** after dropping two keyword-bleed artifacts (see §8).

### 5.3 Sampling — **decided: uniform over both lists, seed 2026**

```python
random.seed(2026)
pairs = [(random.choice(estates), random.choice(schools)) for _ in range(100)]
```
Uniform, not population-weighted, because (a) the brief said "100 random pairs from the list" and (b) block counts are unreliable. Fully reproducible.

**Consequence to state aloud in the viva:** random pairing yields a mean straight-line distance of **11.52 km**, far longer than real school commutes (students mostly attend nearby schools). The distance-banded results (§6.2) are the honest read; the `<5 km` band is the conservative floor.

### 5.4 Travel-time model — **decided: analytic distance-decay, calibrated to LTA**

Used because live routing is blocked (§7). Not a routing engine; a transparent, auditable approximation.

```python
CAR_DETOUR, PT_DETOUR = 1.30, 1.45       # network distance / straight line
PARK_WALK             = 5.0              # min: walk to car + park + walk into school

def v_car(d, peak=True):                 # km/h, rises with trip length (expressway use)
    v = 22 + 20*(1 - exp(-d/7.0))        # d=2 → 27.6 ; d=10 → 37.1 ; d=20 → 40.8
    return v if peak else v*1.12

def v_pt(d):                             # km/h, effective line-haul incl. dwell
    return 16 + 22*(1 - exp(-d/9.0))     # d=3 → 22.9 ; d=8 → 30.2 ; d=15 → 33.4

def car_time(d, peak=True):
    return PARK_WALK + (CAR_DETOUR*d)/v_car(d, peak)*60

def pt_time(d, peak=True):
    if d < 2.5:                                        # single bus, no transfer
        return 6 + (6 if peak else 8) + (PT_DETOUR*d)/18.0*60 + 4
    transfers = 1 if d < 11 else 2
    wait      = 5 if peak else 6
    return (6                                          # access walk
            + wait                                     # initial wait
            + (PT_DETOUR*d)/v_pt(d)*60                 # in-vehicle
            + transfers*(5 if peak else 6)             # transfer penalty
            + 5)                                       # egress walk
```
AM = peak, PM (16:00) = off-peak.

**Validation:** a realistic 4 km school trip returns **34.6 min** by PT against LTA's observed **30–35 min**. Good agreement at the distance where most real trips sit.

### 5.5 Charting — **decided: matplotlib → inline SVG → self-contained HTML**
`svg.fonttype='none'`, `transparent=True`, embedded directly in the HTML so the published page has zero external dependencies (required by the artifact CSP). Theme-aware CSS variables with `prefers-color-scheme` handling.

---

## 6. Results (modelled — supersede these once routed)

### 6.1 Headline

| Metric | Car | Public transport | Gap |
|---|---|---|---|
| Morning trip (arrive 07:30) | 28.4 min | 54.6 min | **+26.2 min** |
| Mean departure from home | 07:02 | 06:35 | **27 min of sleep** |
| Afternoon trip (leave 16:00) | — | — | **+31.2 min** |
| Mean arrival home | 16:26 | 16:57 | — |

- Median AM advantage **28.9 min**; p10 **20.8**, p90 **31.5**
- **PT/car ratio: 1.99×**
- Per school day: **57.4 min**
- Per school year (190 days): **182 hours**
- Over 4 years: **727 hours ≈ 30 entire days**

### 6.2 By distance band (the defensible core)

| Band | n | Car | PT | Advantage |
|---|---|---|---|---|
| < 5 km | 15 | 13.7 | 32.2 | **+18.5** |
| 5–10 km | 24 | 21.6 | 43.8 | **+22.3** |
| 10–15 km | 35 | 29.7 | 57.9 | **+28.2** |
| > 15 km | 26 | 41.6 | 73.0 | **+31.4** |

The advantage **compounds with distance** — which is the sociological payload, because Debs & Cheung's home–school distance priority pushes non-car families toward nearby schools while the car makes the whole island a catchment.

---

## 7. THE BLOCKER — network egress allowlist

The chat sandbox restricts outbound HTTP to a package-manager allowlist. Failures return `403` with body `Host not in allowlist: <host>. Add this host to your network egress settings to allow access.`

| Host | Status |
|---|---|
| `pypi.org`, `raw.githubusercontent.com`, `github.com`, `api.github.com` | ✅ reachable |
| `www.onemap.gov.sg`, `onemap.gov.sg` | ❌ blocked |
| `data.gov.sg` | ❌ blocked |
| `maps.googleapis.com`, `routes.googleapis.com` | ❌ blocked |
| `overpass-api.de`, `router.project-osrm.org`, `api.openrouteservice.org` | ❌ blocked |

Also attempted and closed off:
- `web_fetch` on a constructed OneMap URL → `PERMISSIONS_ERROR` (only URLs from prior search results are fetchable).
- `data.gov.sg` CKAN `datastore_search` via `web_fetch` → `404`.
- GitHub tree API → rate-limited on the shared egress IP (`35.196.153.210`).

**Claude Code is expected to have direct network access — this is the main reason for the handoff.** Verify first with a single call before building anything.

---

## 8. Known data-quality issues (carry these forward)

1. **HDB block counts ≠ true stock.** Bedok 153, Ang Mo Kio 81 are severe undercounts. Mitigated by uniform sampling; would need the official HDB Property Information dataset (`data.gov.sg`) to fix properly.
2. **Two estates dropped** for road-keyword bleed: `Geylang – Choa Chu Kang North 5` (1 block, wrong town) and `Tengah – Plantation Avenue` at lon 103.87 (the `PLANTATION` keyword matched an eastern street). Filter applied: drop Tengah estates with `lon > 103.80`.
3. **Duplicate estate names within a town** where k-means split one road family — e.g. two `Hougang – Hougang Avenue 8`, two `Geylang – Circuit Road`, two `Jurong East Street 21`. Harmless for sampling; cosmetically poor. Fix by appending a cardinal suffix.
4. **School list is name-pattern derived, not authoritative.** 146 entries vs roughly 136 official secondary schools. Built from `INCLUDE`/`EXCLUDE` keyword lists; may retain a specialised or non-secondary institution and may miss a school with an unusual name. `SENG KANG`/`SENGKANG` were deduplicated. `ANGLO-CHINESE SCHOOL` is ambiguous (resolved to the Dover/Independent campus). **Replace with the MOE directory when reachable.**
5. **Source vintage.** `buildings.json` is roughly 2017–2021, so the newest BTOs (Tengah, Punggol Northshore) are under-represented.
6. **Random pairing overstates distance** (mean 11.52 km). Report banded results.
7. **OneMap `drive` has no traffic model** — see §9.2. Uncorrected, it would inflate the car advantage and hand an examiner an easy kill.

---

## 9. OneMap API reference

### 9.1 Auth and limits
- Token supplied by the user; **JWT, 3-day expiry** (the current one expires ~20 Sep 2026, `exp: 1789899532`). Re-mint at `https://www.onemap.gov.sg/apidocs/register`.
- Passed as a header: `Authorization: <token>` (no `Bearer` prefix).
- **Rate limit 300 calls/min.** 400 legs ≈ 2 minutes at full tilt; the script self-throttles to ~4/s.
- Token-free endpoints (basemaps, static map) are irrelevant here; Search, Routing, Reverse Geocode all need the token.

### 9.2 Routing endpoint
```
GET https://www.onemap.gov.sg/api/public/routingsvc/route
```

| Param | Notes |
|---|---|
| `start` | `"lat,lon"` |
| `end` | `"lat,lon"` |
| `routeType` | `drive` \| `pt` \| `walk` \| `cycle` |
| `date` | **`MM-DD-YYYY`** (pt only) |
| `time` | `HH:MM:SS` (pt only) |
| `mode` | `TRANSIT` \| `BUS` \| `RAIL` (pt only) |
| `maxWalkDistance` | metres, e.g. `1200` (pt only) |
| `numItineraries` | e.g. `1` (pt only) |

Response extraction:
- **drive:** `route_summary.total_time` (seconds), `route_summary.total_distance` (metres)
- **pt:** `plan.itineraries[0]` → `duration`, `walkTime`, `waitingTime`, `transitTime` (all seconds), `transfers` (int)

**Two critical quirks:**
1. **`pt` is depart-at only.** The 07:30 arrival must be solved by iteration: seed a departure guess, route it, set the next guess to the returned duration, repeat until `|error| ≤ 2 min`. Two or three iterations converge.
2. **`drive` returns free-flow times with no congestion model**, while `pt` uses real timetables. Comparing them raw is **rigged in the car's favour**. Current correction: `×1.35` AM peak, `×1.15` PM, plus a 5-min park-and-walk penalty. This multiplier is a placeholder and is the single weakest link in the whole analysis — see §10 item 2.

---

## 10. Immediate next steps, in priority order

### 1. Run the real routing (highest value)
`run_onemap_routing.py` is written and ready. From a directory containing the three CSVs:
```bash
pip install requests
python run_onemap_routing.py --token "<ONEMAP_JWT>" --pairs buying_time_100_pairs.csv
# flags: --peak-factor 1.35  --pm-factor 1.15  --limit N (smoke test)
```
Smoke-test with `--limit 3` first. It writes `onemap_results.csv` and prints a paste-ready summary block.
**Expected outcome:** AM advantage in the **22–30 min** range. If it lands there, the model is validated and that validation is itself a strong point to make in the viva. If it diverges materially, the routed numbers win.

### 2. Replace the drive peak-factor fudge with real traffic data
The `×1.35` is the most attackable number in the analysis. Options, best first:
- **TomTom** (`tomtom-routing`, already connected to the user's account) — has historical and live traffic speeds by time of day. Route a calibration subset, regress routed-peak against OneMap free-flow, and either fit a proper factor or replace the car leg outright. **The user has not yet authorised firing this connector — ask first.**
- Google Directions API with `departure_time` + `traffic_model=best_guess` (needs a billing-enabled key).
- Fall back to publishing the uncorrected number *and* the corrected one as a sensitivity band.

### 3. Fix the school list
Pull the MOE directory once `data.gov.sg` is reachable:
```
https://data.gov.sg/api/action/datastore_search?resource_id=d_688b934f82c1059ed0a6993d2a829089
```
(CKAN `datastore_search` returned 404 via `web_fetch`; try the v2 `api-open.data.gov.sg` path or the CSV download.) Filter to `mainlevel_code == 'SECONDARY'`, join to coordinates by postal code. Replaces the keyword heuristic and fixes the 146-vs-136 discrepancy.

### 4. Fix HDB estate weighting
Pull **HDB Property Information** from `data.gov.sg`, join on `(BLK_NO, ROAD_NAME)` to get authoritative HDB blocks plus **dwelling-unit counts**. That enables population-weighted estate centroids and optional population-weighted sampling as a robustness check alongside the uniform draw.

### 5. Rebuild the dashboard with routed data
Regenerate charts A–F and the KPI block from `onemap_results.csv`. Keep the existing structure; swap the "modelled, not routed" warning for a short method note describing the iteration procedure and the drive-time correction. Republish.

### 6. Optional extensions (only if time permits before 14:00 Friday)
- Sensitivity analysis: vary `PT_DETOUR`, transfer penalty, and peak factor; report the advantage as a range rather than a point estimate.
- A "realistic assignment" counterfactual: pair each estate with its *nearest* school instead of a random one, to bound the advantage from below under actual enrolment patterns.
- Extend to the other three domains (tuition travel, polyclinic vs private GP catchments) — almost certainly out of scope before the deadline.

---

## 11. File inventory

All under `/mnt/user-data/outputs/`:

| File | Description |
|---|---|
| `buying_time_dashboard.html` | Self-contained visual dashboard, 6 charts + full results table. Published at `https://claude.ai/artifact/TzWEaNF56iR3dU5dSDUxPM` |
| `buying_time_100_pairs.csv` | The 100 sampled pairs with modelled times |
| `hdb_estates_142.csv` | Estate list |
| `secondary_schools_146.csv` | School list |
| `run_onemap_routing.py` | Ready-to-run OneMap routing script |

Working files under `/home/claude/data/`: `buildings.json`, `hdb_points.json`, `estates.json`, `schools_final.json`, `results.json`, `charts.json`, `stats.json`.

### Schemas

**`hdb_estates_142.csv`**
```
estate       TEXT   "Sengkang – Anchorvale Road"
town         TEXT   "Sengkang"
lat          FLOAT  1.393900
lon          FLOAT  103.888880
hdb_blocks   INT    186          -- member blocks in cluster
```

**`secondary_schools_146.csv`**
```
school       TEXT   "Ngee Ann Secondary School"
postal       TEXT   "520101"     -- keep as TEXT, leading zeros
lat          FLOAT
lon          FLOAT
address      TEXT
```

**`buying_time_100_pairs.csv`** (modelled)
```
id            INT     1..100
estate        TEXT    FK -> hdb_estates_142.estate
town          TEXT
school        TEXT    FK -> secondary_schools_146.school
km            FLOAT   haversine straight-line, home->school
car_am_min    FLOAT   door-to-door, AM peak
pt_am_min     FLOAT
adv_am_min    FLOAT   = pt_am_min - car_am_min
depart_car    TEXT    "HH:MM"  = 07:30 - car_am_min
depart_pt     TEXT    "HH:MM"  = 07:30 - pt_am_min
car_pm_min    FLOAT
pt_pm_min     FLOAT
arrive_car    TEXT    "HH:MM"  = 16:00 + car_pm_min
arrive_pt     TEXT    "HH:MM"  = 16:00 + pt_pm_min
adv_day_min   FLOAT   = adv_am_min + adv_pm_min
```

**`onemap_results.csv`** (routed — target output, superset of the above)
```
id, estate, town, school, km,
car_am_min, pt_am_min, adv_am_min,
car_pm_min, pt_pm_min, adv_pm_min, adv_day_min,
depart_car, depart_pt, arrive_car, arrive_pt,
pt_walk_min      FLOAT   walk component, AM
pt_wait_min      FLOAT   waiting component, AM
pt_transfers     INT     transfer count, AM
car_raw_am       FLOAT   uncorrected OneMap free-flow drive minutes
```

---

## 12. Supporting research findings (for the presentation, not the pipeline)

Verified figures the professor may probe:

- **COE Cat A record S$133,009** (bidding closed 9 Sep 2026); Cat B S$135,001; Cat E S$137,890. Roughly fourfold in a decade (~S$37,000 average in 2017). Volatile: dipped to S$106,320 in Feb 2026 before rebounding.
- Mass-market **Toyota Corolla now S$170,000–220,000** on-the-road; total ownership above S$200,000. Same car ≈ US$22,000 in the US.
- **36.3% of resident households own a car** (HES 2023), but only **17.0% of the lowest income quintile** vs 55.4% of married couples with young children.
- Vehicle growth rate **0% since Feb 2018**; ~20,000 additional COEs injected from Feb 2025 to smooth the supply trough.
- **Healthcare:** median wait to a public Specialist Outpatient Clinic in 2024 was **35 days subsidised vs 12 days unsubsidised** — money buys three weeks of earlier diagnosis.
- **Tuition:** households spent **S$1.8 billion in 2023** (S$104.80/month average); top quintile S$162.60/month vs bottom quintile S$36.30 — a **4.5× gap**.
- **Domestic labour:** **286,300 MDWs** (MOM, Dec 2023); 16.2% of resident households, 30.0% of married couples with young children. Levy S$300/month, S$60 under concession.
- **Social capital:** IPS study — private-housing/elite-school respondents had ~2.6 ties to people of more modest backgrounds vs ~0.8 for HDB/non-elite-school respondents.

**The counter-argument that must be pre-empted:** the COE can be read as an *egalitarian* device — capping the fleet, pricing cars as luxuries, avoiding American-style car-dependency that taxes the poor, with revenue funding subsidised public transport. Concede the design intent, then deploy the residual: the 45-minute-city target still misses ~a third of workers, and the health, tuition, helper and social-tie gaps persist regardless. The thesis is about the **portfolio** of time-buying, not the car alone — block one channel and money re-routes into the others.

**Citation corrections to make before presenting:** Debs's co-author is **Hoi Shan Cheung**; the RSIS fourth author is **Pravin Prakash**.
