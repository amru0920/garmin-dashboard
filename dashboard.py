#!/usr/bin/env python3
"""Self-contained running/training dashboard, built from Garmin Connect data.

Reuses the OAuth tokens already cached by garmin-mcp / garmin-mcp-auth (default
~/.garminconnect, or $GARMINTOKENS) -- never prompts for a password. Run this
script any time to refresh data and rebuild index.html:

    python dashboard.py

Then open index.html in a browser. No Claude Code / MCP server needed to run it.

Data notes (checked against this account before writing this script):
  - Garmin's official Firstbeat training status (CTL/ATL/TSB), HRV, training
    readiness, endurance score and lactate threshold are NOT available on this
    account's devices (Forerunner 45 / 45S / 55 -- no HRV sensor, no Firstbeat
    training-status support). Sleep is also not being recorded (not worn
    overnight). Rather than ship empty charts, this script:
      * computes an ESTIMATED Fitness/Fatigue/Form (CTL/ATL/TSB-shaped) trend
        from a Banister-TRIMP training load derived from each run's heart
        rate and duration -- clearly labelled as an estimate, not Garmin's
        number.
      * substitutes Body Battery + stress for the missing HRV/sleep recovery
        signals.
  - VO2 max, race predictions, resting HR, stress, body battery, and full
    activity/splits data ARE available and are used directly.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import os
import statistics
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from og_image import generate_og_image
from training_plan import (
    generate_default_plan,
    load_plan_config,
    merge_plan_with_actuals,
    save_plan_config,
)

# --------------------------------------------------------------------------
# Config -- edit these for your race and stats.
# --------------------------------------------------------------------------

RACE_NAME = "Penang Bridge Marathon"
RACE_DATE = "2026-11-15"
SITE_URL = "https://garmin-dashboard-ezq.pages.dev/"  # for og:image / og:url -- must be absolute

HEIGHT_CM = 168
WEIGHT_KG = 54

PERSONAL_BESTS = {
    # distance_km: time_seconds (None if you don't have one yet)
    "5K": 20 * 60 + 47,
    "10K": 41 * 60 + 36,
    "Half Marathon": None,
    "Marathon": None,
}

MILEAGE_WEEKS = 12          # weeks shown in weekly-mileage / training-load charts
RECOVERY_DAYS = 42          # days shown in the recovery panel
ACTIVITY_LOOKBACK_DAYS = 130  # fetch window for activities (extra buffer feeds CTL ramp-up)
RECENT_RUNS_DAYS = 28        # window for the Runs table

SCRIPT_DIR = Path(__file__).resolve().parent
CACHE_PATH = SCRIPT_DIR / "dashboard_cache.json"
OUTPUT_PATH = SCRIPT_DIR / "index.html"
OG_IMAGE_PATH = SCRIPT_DIR / "og-image.png"
PLAN_CONFIG_PATH = SCRIPT_DIR / "training_plan_config.json"

RUNNING_TYPE_KEYS = {
    "running", "trail_running", "treadmill_running", "track_running",
    "street_running", "ultra_run", "indoor_running", "virtual_run",
}

# --------------------------------------------------------------------------
# Auth -- cached tokens only, never prompts for a password.
# --------------------------------------------------------------------------

def get_token_path() -> str:
    raw = os.getenv("GARMINTOKENS") or "~/.garminconnect"
    expanded = os.path.expandvars(raw).replace("${HOME}", os.path.expanduser("~"))
    return os.path.expanduser(expanded)


def login():
    from garminconnect import (
        Garmin,
        GarminConnectAuthenticationError,
        GarminConnectConnectionError,
        GarminConnectTooManyRequestsError,
    )

    token_path = get_token_path()
    if not os.path.exists(token_path):
        print(
            f"ERROR: no cached Garmin tokens found at '{token_path}'.\n"
            "Run 'garmin-mcp-auth' (or authenticate the garmin-mcp server once) "
            "to create them, then re-run this script.",
            file=sys.stderr,
        )
        sys.exit(1)

    client = Garmin()
    try:
        client.login(token_path)
    except (
        FileNotFoundError,
        GarminConnectAuthenticationError,
        GarminConnectConnectionError,
        GarminConnectTooManyRequestsError,
    ) as exc:
        print(
            f"ERROR: could not log in with cached tokens at '{token_path}': {exc}\n"
            "Tokens may have expired -- re-run 'garmin-mcp-auth' to refresh them.",
            file=sys.stderr,
        )
        sys.exit(1)
    return client


# --------------------------------------------------------------------------
# Cache
# --------------------------------------------------------------------------

def load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"daily_stats": {}, "splits": {}, "predictions_history": []}


def save_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, indent=2), encoding="utf-8")


# --------------------------------------------------------------------------
# Fetch
# --------------------------------------------------------------------------

def fetch_activities(client, start_date: str, end_date: str) -> list[dict]:
    try:
        raw = client.get_activities_by_date(start_date, end_date, sortorder="asc") or []
    except Exception as exc:
        print(f"WARNING: failed to fetch activities: {exc}", file=sys.stderr)
        return []

    out = []
    for a in raw:
        type_key = (a.get("activityType") or {}).get("typeKey", "")
        out.append({
            "id": a.get("activityId"),
            "name": a.get("activityName") or "",
            "type": type_key,
            "is_running": type_key in RUNNING_TYPE_KEYS,
            "start_time_local": a.get("startTimeLocal"),
            "distance_m": a.get("distance") or 0.0,
            "duration_s": a.get("duration") or 0.0,
            "moving_duration_s": a.get("movingDuration") or a.get("duration") or 0.0,
            "avg_hr": a.get("averageHR"),
            "max_hr": a.get("maxHR"),
            "calories": a.get("calories"),
        })
    return out


def fetch_splits_cached(client, activities: list[dict], cache: dict) -> None:
    """Populate cache['splits'][activity_id] for running activities, reusing cache."""
    splits_cache = cache.setdefault("splits", {})
    running = [a for a in activities if a["is_running"] and a["distance_m"] >= 800]
    fetched = 0
    for a in running:
        key = str(a["id"])
        if key in splits_cache:
            continue
        try:
            raw = client.get_activity_splits(a["id"]) or {}
        except Exception:
            splits_cache[key] = []
            continue
        laps = []
        for lap in raw.get("lapDTOs", []):
            laps.append({
                "distance_m": lap.get("distance") or 0.0,
                "duration_s": lap.get("duration") or 0.0,
                "moving_duration_s": lap.get("movingDuration") or lap.get("duration") or 0.0,
                "avg_speed_mps": lap.get("averageSpeed"),
                "avg_hr": lap.get("averageHR"),
                "intensity_type": lap.get("intensityType"),
            })
        splits_cache[key] = laps
        fetched += 1
    if fetched:
        print(f"Fetched splits for {fetched} new activities.")


def fetch_daily_stats_cached(client, days: list[str], cache: dict) -> None:
    """Populate cache['daily_stats'][date] for the given dates, skipping cached
    days except the most recent 2 (which may still be syncing)."""
    daily = cache.setdefault("daily_stats", {})
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    fetched = 0
    for d in days:
        if d in daily and d not in (today, yesterday):
            continue
        try:
            stats = client.get_stats(d) or {}
        except Exception:
            continue
        daily[d] = {
            "resting_hr": stats.get("restingHeartRate"),
            "avg_stress": stats.get("averageStressLevel"),
            "max_stress": stats.get("maxStressLevel"),
            "steps": stats.get("totalSteps"),
        }
        fetched += 1
    if fetched:
        print(f"Fetched daily wellness stats for {fetched} day(s).")


def fetch_body_battery(client, start_date: str, end_date: str) -> list[dict]:
    """Garmin's body-battery endpoint rejects date ranges above ~28 days
    ("requested date range is too big"), so fetch in chunks and merge."""
    CHUNK_DAYS = 28
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    out: list[dict] = []
    chunk_start = start
    while chunk_start <= end:
        chunk_end = min(chunk_start + timedelta(days=CHUNK_DAYS - 1), end)
        try:
            raw = client.get_body_battery(chunk_start.isoformat(), chunk_end.isoformat()) or []
        except Exception as exc:
            print(f"WARNING: failed to fetch body battery for {chunk_start}..{chunk_end}: {exc}", file=sys.stderr)
            raw = []
        out.extend(
            {"date": d.get("date"), "charged": d.get("charged"), "drained": d.get("drained")}
            for d in raw
            if d.get("date")
        )
        chunk_start = chunk_end + timedelta(days=1)
    return out


def fetch_vo2max_trend(client, start_date: str, end_date: str) -> list[dict]:
    metrics_url = getattr(client, "garmin_connect_metrics_url", None)
    if not metrics_url:
        return []
    try:
        raw = client.connectapi(f"{metrics_url}/{start_date}/{end_date}") or []
    except Exception as exc:
        print(f"WARNING: failed to fetch VO2max trend: {exc}", file=sys.stderr)
        return []

    points: dict[str, float] = {}
    items = raw if isinstance(raw, list) else [raw]
    for item in items:
        if not isinstance(item, dict):
            continue
        generic = item.get("generic") or {}
        value = generic.get("vo2MaxPreciseValue") or generic.get("vo2MaxValue")
        cal_date = generic.get("calendarDate") or item.get("calendarDate")
        if value and cal_date:
            points.setdefault(cal_date, round(float(value), 1))
    return [{"date": d, "value": v} for d, v in sorted(points.items())]


def fetch_race_predictions(client) -> Optional[dict]:
    try:
        raw = client.get_race_predictions()
    except Exception as exc:
        print(f"WARNING: failed to fetch race predictions: {exc}", file=sys.stderr)
        return None
    if not raw:
        return None
    return {
        "date": raw.get("calendarDate") or date.today().isoformat(),
        "5k_s": raw.get("time5K"),
        "10k_s": raw.get("time10K"),
        "half_s": raw.get("timeHalfMarathon"),
        "marathon_s": raw.get("timeMarathon"),
    }


def fetch_user_profile(client) -> dict:
    try:
        profile = client.get_user_profile() or {}
    except Exception:
        profile = {}
    user_data = profile.get("userData") or {}
    return {
        "gender": user_data.get("gender"),
        "birth_date": user_data.get("birthDate"),
        "vo2max_running": user_data.get("vo2MaxRunning"),
    }


def fetch_intensity_minutes(client, on_date: str) -> Optional[dict]:
    try:
        raw = client.get_intensity_minutes_data(on_date)
    except Exception as exc:
        print(f"WARNING: failed to fetch intensity minutes: {exc}", file=sys.stderr)
        return None
    if not raw:
        return None
    return {
        "weekly_moderate": raw.get("weeklyModerate"),
        "weekly_vigorous": raw.get("weeklyVigorous"),
        "weekly_total": raw.get("weeklyTotal"),
        "week_goal": raw.get("weekGoal"),
    }


def fetch_fitness_age(client, on_date: str) -> Optional[dict]:
    try:
        raw = client.get_fitnessage_data(on_date)
    except Exception as exc:
        print(f"WARNING: failed to fetch fitness age: {exc}", file=sys.stderr)
        return None
    if not raw or raw.get("fitnessAge") is None:
        return None
    return {
        "fitness_age": raw.get("fitnessAge"),
        "chronological_age": raw.get("chronologicalAge"),
        "achievable_fitness_age": raw.get("achievableFitnessAge"),
    }


def compute_age(birth_date: Optional[str]) -> Optional[int]:
    if not birth_date:
        return None
    try:
        born = date.fromisoformat(birth_date)
    except ValueError:
        return None
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def fetch_floors_available(client, on_date: str) -> bool:
    """This account's devices (Forerunner 45/45S/55) have no barometric
    altimeter, so this always comes back empty -- probed once per run so the
    UI can say so plainly instead of silently showing nothing."""
    try:
        raw = client.get_floors(on_date) or {}
    except Exception:
        return False
    return bool(raw.get("floorValuesArray"))


# --------------------------------------------------------------------------
# Compute -- derived metrics
# --------------------------------------------------------------------------

def estimate_threshold_hr(activities: list[dict], splits_cache: dict) -> tuple[float, str]:
    """Estimate LTHR from ACTIVE laps of runs the user tagged THRESHOLD/TEMPO."""
    weighted_sum = 0.0
    weighted_dur = 0.0
    for a in activities:
        if not a["is_running"]:
            continue
        name = (a["name"] or "").lower()
        if "threshold" not in name and "tempo" not in name:
            continue
        for lap in splits_cache.get(str(a["id"]), []):
            if lap.get("intensity_type") != "ACTIVE":
                continue
            hr, dur = lap.get("avg_hr"), lap.get("moving_duration_s") or lap.get("duration_s")
            if hr and dur:
                weighted_sum += hr * dur
                weighted_dur += dur

    max_hr_observed = max(
        (a["max_hr"] for a in activities if a.get("max_hr")), default=0
    )

    if weighted_dur > 0:
        thr = weighted_sum / weighted_dur
        return round(thr, 1), "derived from your THRESHOLD/TEMPO-tagged runs"

    if max_hr_observed:
        thr = 0.88 * max_hr_observed
        return round(thr, 1), "estimated as 88% of your observed max HR (no THRESHOLD/TEMPO-tagged runs found)"

    return 165.0, "fallback default (no data available to estimate this)"


def estimate_max_hr(activities: list[dict], birth_date: Optional[str]) -> float:
    observed = max((a["max_hr"] for a in activities if a.get("max_hr")), default=0)
    formula = 220.0
    if birth_date:
        try:
            born = date.fromisoformat(birth_date)
            age = (date.today() - born).days / 365.25
            formula = 220.0 - age
        except ValueError:
            pass
    return max(observed, formula)


def banister_trimp(duration_min: float, avg_hr: float, resting_hr: float, max_hr: float, gender: str) -> float:
    if max_hr <= resting_hr or duration_min <= 0 or not avg_hr:
        return 0.0
    hrr = (avg_hr - resting_hr) / (max_hr - resting_hr)
    hrr = min(max(hrr, 0.0), 1.05)
    if gender == "FEMALE":
        k, b = 1.67, 0.86
    else:
        k, b = 1.92, 0.64
    return duration_min * hrr * b * math.exp(k * hrr)


def compute_training_load_series(
    activities: list[dict], daily_stats: dict, resting_hr_default: float,
    max_hr: float, gender: str, start: date, end: date,
) -> list[dict]:
    """Estimated CTL/ATL/TSB, Banister-TRIMP based (Garmin's official Firstbeat
    training status isn't available on this account's devices)."""
    daily_load: dict[str, float] = {}
    for a in activities:
        if not a["is_running"] or not a.get("avg_hr"):
            continue
        d = (a["start_time_local"] or "")[:10]
        if not d:
            continue
        rhr = (daily_stats.get(d) or {}).get("resting_hr") or resting_hr_default
        trimp = banister_trimp(a["moving_duration_s"] / 60.0, a["avg_hr"], rhr, max_hr, gender)
        daily_load[d] = daily_load.get(d, 0.0) + trimp

    series = []
    ctl = atl = 0.0
    cur = start
    while cur <= end:
        d = cur.isoformat()
        load = daily_load.get(d, 0.0)
        ctl += (load - ctl) / 42.0
        atl += (load - atl) / 7.0
        series.append({
            "date": d,
            "load": round(load, 1),
            "ctl": round(ctl, 1),
            "atl": round(atl, 1),
            "tsb": round(ctl - atl, 1),
        })
        cur += timedelta(days=1)
    return series


def compute_weekly_mileage(activities: list[dict], weeks: int, today: date) -> list[dict]:
    week_start_of = lambda d: d - timedelta(days=d.weekday())  # Monday start
    this_week_start = week_start_of(today)
    earliest = this_week_start - timedelta(weeks=weeks - 1)

    buckets: dict[str, float] = {}
    counts: dict[str, int] = {}
    cur = earliest
    while cur <= this_week_start:
        buckets[cur.isoformat()] = 0.0
        counts[cur.isoformat()] = 0
        cur += timedelta(weeks=1)

    for a in activities:
        if not a["is_running"]:
            continue
        d = (a["start_time_local"] or "")[:10]
        if not d:
            continue
        try:
            adate = date.fromisoformat(d)
        except ValueError:
            continue
        wk = week_start_of(adate).isoformat()
        if wk in buckets:
            buckets[wk] += a["distance_m"] / 1000.0
            counts[wk] += 1

    weeks_sorted = sorted(buckets.keys())
    values = [round(buckets[w], 1) for w in weeks_sorted]
    trend = [max(0.0, t) for t in linear_trend(values)]
    return [
        {"week_start": w, "km": buckets[w] and round(buckets[w], 1) or 0.0,
         "runs": counts[w], "trend_km": round(t, 1)}
        for w, t in zip(weeks_sorted, trend)
    ]


def linear_trend(values: list[float]) -> list[float]:
    n = len(values)
    if n < 2:
        return values[:]
    xs = list(range(n))
    mean_x = sum(xs) / n
    mean_y = sum(values) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, values))
    den = sum((x - mean_x) ** 2 for x in xs) or 1.0
    slope = num / den
    intercept = mean_y - slope * mean_x
    return [slope * x + intercept for x in xs]


def classify_effort(avg_hr: Optional[float], laps: list[dict], threshold_hr: float) -> tuple[str, Optional[float]]:
    hard_cut = 0.95 * threshold_hr
    mod_cut = 0.85 * threshold_hr

    usable_laps = [l for l in laps if l.get("avg_hr") and (l.get("moving_duration_s") or l.get("duration_s"))]
    total = sum(l.get("moving_duration_s") or l.get("duration_s") for l in usable_laps)
    if usable_laps and total > 0:
        hard = sum((l.get("moving_duration_s") or l.get("duration_s"))
                    for l in usable_laps if l["avg_hr"] >= hard_cut)
        moderate = sum((l.get("moving_duration_s") or l.get("duration_s"))
                        for l in usable_laps if mod_cut <= l["avg_hr"] < hard_cut)
        hard_pct = round(hard / total * 100, 1)
        moderate_pct = moderate / total * 100
        if hard_pct >= 15:
            return "hard", hard_pct
        if hard_pct + moderate_pct >= 40:
            return "moderate", hard_pct
        return "easy", hard_pct

    if not avg_hr:
        return "unknown", None
    if avg_hr >= hard_cut:
        return "hard", 100.0
    if avg_hr >= mod_cut:
        return "moderate", 0.0
    return "easy", 0.0


def compute_decoupling(laps: list[dict], distance_m: float, moving_duration_s: float) -> Optional[float]:
    """Aerobic decoupling (% drop in pace/HR efficiency, 1st half vs 2nd half)
    for long runs only (>=8km or >=40min)."""
    if distance_m < 8000 and moving_duration_s < 2400:
        return None
    usable = [l for l in laps if l.get("distance_m", 0) >= 300 and l.get("avg_hr") and l.get("avg_speed_mps")]
    if len(usable) < 4:
        return None
    half = len(usable) // 2
    first, second = usable[:half], usable[half:]

    def efficiency(laps_: list[dict]) -> Optional[float]:
        dur = sum(l.get("moving_duration_s") or l.get("duration_s") or 0 for l in laps_)
        if dur <= 0:
            return None
        hr = sum(l["avg_hr"] * (l.get("moving_duration_s") or l.get("duration_s") or 0) for l in laps_) / dur
        speed = sum(l["avg_speed_mps"] * (l.get("moving_duration_s") or l.get("duration_s") or 0) for l in laps_) / dur
        if hr <= 0:
            return None
        return speed / hr

    ef1, ef2 = efficiency(first), efficiency(second)
    if not ef1 or not ef2:
        return None
    return round((ef1 - ef2) / ef1 * 100, 1)


def build_runs(activities: list[dict], splits_cache: dict, threshold_hr: float, window_start: date) -> list[dict]:
    runs = []
    for a in activities:
        if not a["is_running"] or a["distance_m"] < 500:
            continue
        d_str = (a["start_time_local"] or "")[:10]
        try:
            d = date.fromisoformat(d_str)
        except ValueError:
            continue
        if d < window_start:
            continue
        laps = splits_cache.get(str(a["id"]), [])
        effort, hard_pct = classify_effort(a.get("avg_hr"), laps, threshold_hr)
        # Decoupling only means something for continuous steady-state efforts;
        # on an interval/threshold session the first-half/second-half split
        # just measures the workout structure, not aerobic drift.
        decoupling = (
            compute_decoupling(laps, a["distance_m"], a["moving_duration_s"])
            if effort != "hard" else None
        )
        distance_km = a["distance_m"] / 1000.0
        pace_s_per_km = (a["moving_duration_s"] / distance_km) if distance_km > 0 else None
        runs.append({
            "id": a["id"],
            "date": d_str,
            "name": a["name"],
            "distance_km": round(distance_km, 2),
            "duration_s": a["duration_s"],
            "moving_duration_s": a["moving_duration_s"],
            "pace_s_per_km": round(pace_s_per_km, 1) if pace_s_per_km else None,
            "avg_hr": a.get("avg_hr"),
            "max_hr": a.get("max_hr"),
            "effort": effort,
            "hard_pct": hard_pct,
            "decoupling_pct": decoupling,
        })
    runs.sort(key=lambda r: r["date"], reverse=True)
    return runs


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> None:
    print("Logging in to Garmin Connect with cached tokens...")
    client = login()
    print("Logged in.")

    cache = load_cache()
    today = date.today()

    activity_start = (today - timedelta(days=ACTIVITY_LOOKBACK_DAYS)).isoformat()
    activity_end = today.isoformat()
    print(f"Fetching activities from {activity_start} to {activity_end}...")
    activities = fetch_activities(client, activity_start, activity_end)
    print(f"Fetched {len(activities)} activities.")

    fetch_splits_cached(client, activities, cache)

    recovery_start = today - timedelta(days=RECOVERY_DAYS - 1)
    recovery_days = [(recovery_start + timedelta(days=i)).isoformat() for i in range(RECOVERY_DAYS)]
    print(f"Fetching daily wellness stats for the last {RECOVERY_DAYS} days (cached incrementally)...")
    fetch_daily_stats_cached(client, recovery_days, cache)

    print("Fetching body battery...")
    body_battery = fetch_body_battery(client, recovery_start.isoformat(), today.isoformat())

    print("Fetching VO2max trend...")
    vo2max_trend = fetch_vo2max_trend(
        client, (today - timedelta(days=ACTIVITY_LOOKBACK_DAYS)).isoformat(), today.isoformat()
    )

    print("Fetching race predictions...")
    predictions = fetch_race_predictions(client)
    if predictions:
        history = cache.setdefault("predictions_history", [])
        if not history or history[-1]["date"] != predictions["date"]:
            history.append(predictions)

    profile = fetch_user_profile(client)

    print("Fetching intensity minutes...")
    intensity_minutes = fetch_intensity_minutes(client, today.isoformat())

    print("Fetching fitness age...")
    fitness_age = fetch_fitness_age(client, today.isoformat())

    floors_available = fetch_floors_available(client, today.isoformat())

    save_cache(cache)
    print("Cache saved.")

    # ---- derived metrics ----
    threshold_hr, threshold_source = estimate_threshold_hr(activities, cache["splits"])
    max_hr = estimate_max_hr(activities, profile.get("birth_date"))
    resting_hrs = [v["resting_hr"] for v in cache["daily_stats"].values() if v.get("resting_hr")]
    resting_hr_default = statistics.median(resting_hrs) if resting_hrs else 60.0
    gender = profile.get("gender") or "MALE"

    load_window_start = today - timedelta(weeks=MILEAGE_WEEKS) - timedelta(days=7)
    training_load = compute_training_load_series(
        activities, cache["daily_stats"], resting_hr_default, max_hr, gender,
        load_window_start, today,
    )
    # trim display window to MILEAGE_WEEKS
    display_start = (today - timedelta(weeks=MILEAGE_WEEKS)).isoformat()
    training_load = [p for p in training_load if p["date"] >= display_start]

    weekly_mileage = compute_weekly_mileage(activities, MILEAGE_WEEKS, today)

    runs_window_start = today - timedelta(weeks=MILEAGE_WEEKS)
    runs = build_runs(activities, cache["splits"], threshold_hr, runs_window_start)

    rhr_series = []
    stress_series = []
    steps_series = []
    for d in recovery_days:
        stats = cache["daily_stats"].get(d) or {}
        if stats.get("resting_hr"):
            rhr_series.append({"date": d, "value": stats["resting_hr"]})
        if stats.get("avg_stress") is not None:
            stress_series.append({"date": d, "avg": stats["avg_stress"], "max": stats.get("max_stress")})
        if stats.get("steps"):
            steps_series.append({"date": d, "value": stats["steps"]})
    rhr_values = [p["value"] for p in rhr_series]
    for i, p in enumerate(rhr_series):
        window = rhr_values[max(0, i - 6):i + 1]
        p["rolling7"] = round(sum(window) / len(window), 1)

    days_left = (date.fromisoformat(RACE_DATE) - today).days
    weeks_left = days_left / 7.0

    latest_load = training_load[-1] if training_load else {"ctl": 0, "atl": 0, "tsb": 0}
    week_km = weekly_mileage[-1]["km"] if weekly_mileage else 0.0
    latest_vo2 = vo2max_trend[-1]["value"] if vo2max_trend else profile.get("vo2max_running")
    latest_rhr = rhr_series[-1]["value"] if rhr_series else None
    latest_stress = stress_series[-1]["avg"] if stress_series else None

    # ---- training plan: generated once, then never silently overwritten ----
    plan_config = None if REGEN_PLAN else load_plan_config(PLAN_CONFIG_PATH)
    if plan_config is None:
        plan_config = generate_default_plan(RACE_DATE, today, weekly_mileage, latest_load.get("ctl", 0))
        save_plan_config(PLAN_CONFIG_PATH, plan_config)
        print(f"{'Regenerated' if REGEN_PLAN else 'Generated'} {PLAN_CONFIG_PATH.name}.")
    plan_weeks = merge_plan_with_actuals(plan_config, weekly_mileage, today)

    data = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "race": {"name": RACE_NAME, "date": RACE_DATE, "days_left": days_left, "weeks_left": round(weeks_left, 1)},
        "profile": {
            "height_cm": HEIGHT_CM, "weight_kg": WEIGHT_KG,
            "threshold_hr": threshold_hr, "threshold_source": threshold_source,
            "max_hr": round(max_hr), "resting_hr_baseline": round(resting_hr_default),
            "age": compute_age(profile.get("birth_date")), "gender": gender,
        },
        "personal_bests": PERSONAL_BESTS,
        "predictions": {
            "current": predictions,
            "history": cache.get("predictions_history", []),
        },
        "vo2max": {"current": latest_vo2, "trend": vo2max_trend},
        "weekly_mileage": weekly_mileage,
        "training_load": training_load,
        "wellness": {
            "rhr": rhr_series,
            "stress": stress_series,
            "body_battery": body_battery,
            "steps": steps_series,
            "intensity_minutes": intensity_minutes,
            "fitness_age": fitness_age,
            "floors_available": floors_available,
        },
        "plan": {
            "weeks": plan_weeks,
            "baseline_weekly_km": plan_config.get("baseline_weekly_km"),
            "generated_on": plan_config.get("generated_on"),
        },
        "runs": runs,
        "recent_runs_days": RECENT_RUNS_DAYS,
        "stat_tiles": {
            "fitness": latest_load.get("ctl", 0),
            "fatigue": latest_load.get("atl", 0),
            "form": latest_load.get("tsb", 0),
            "week_km": round(week_km, 1),
            "vo2max": latest_vo2,
            "resting_hr": latest_rhr,
            "avg_stress": latest_stress,
        },
        "missing_data_note": (
            "Garmin's official training status (CTL/ATL/TSB), HRV, training readiness "
            "and sleep are not available on this account's devices (Forerunner 45 / 45S / 55). "
            "Fitness/Fatigue/Form below is an estimate computed from heart rate and duration, "
            "not Garmin's own metric."
        ),
    }

    print("Generating OG image...")
    generate_og_image(data, OG_IMAGE_PATH)

    print("Rendering index.html...")
    page = render_html(data)
    OUTPUT_PATH.write_text(page, encoding="utf-8")
    print(f"Done. Wrote {OUTPUT_PATH}")
    print(f"Open it with: file:///{OUTPUT_PATH.as_posix()}")

    if PUSH_ENABLED:
        deploy()


# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------

def render_html(data: dict) -> str:
    from dashboard_template import TEMPLATE

    def fmt(v):
        return f"{v:.1f}" if isinstance(v, (int, float)) else "?"

    stat = data["stat_tiles"]
    og_title = f"Training Dashboard — {data['race']['days_left']} days to {data['race']['name']}"
    og_desc = (
        f"Fitness {fmt(stat.get('fitness'))} · Fatigue {fmt(stat.get('fatigue'))} · "
        f"Form {fmt(stat.get('form'))} · VO2max {fmt(stat.get('vo2max'))}"
    )
    og_image_url = SITE_URL.rstrip("/") + "/" + OG_IMAGE_PATH.name

    rendered = TEMPLATE.replace("__DASHBOARD_DATA__", json.dumps(data))
    rendered = rendered.replace("__OG_TITLE__", html.escape(og_title))
    rendered = rendered.replace("__OG_DESC__", html.escape(og_desc))
    rendered = rendered.replace("__OG_IMAGE_URL__", html.escape(og_image_url))
    rendered = rendered.replace("__OG_URL__", html.escape(SITE_URL))
    return rendered


# --------------------------------------------------------------------------
# Deploy -- commit + push only the built index.html, never dashboard.py's own
# source. Auto-committing source from an unattended run risks pushing a
# half-finished edit; the site build is the only thing this loop should own.
# Never raises -- a git/network failure must not stop the local rebuild from
# succeeding, especially when run unattended (Task Scheduler).
# --------------------------------------------------------------------------

def _run_git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=SCRIPT_DIR, capture_output=True, text=True,
    )


def deploy() -> None:
    if _run_git("rev-parse", "--is-inside-work-tree").returncode != 0:
        print("WARNING: not a git repository -- skipping commit/push.", file=sys.stderr)
        return

    if _run_git("remote", "get-url", "origin").returncode != 0:
        print(
            "WARNING: no 'origin' remote configured yet -- built index.html locally "
            "but skipped push. Set up the GitHub repo and 'git remote add origin ...' "
            "to enable auto-deploy.",
            file=sys.stderr,
        )
        return

    files = ["index.html"]
    if OG_IMAGE_PATH.exists():
        files.append(OG_IMAGE_PATH.name)
    if PLAN_CONFIG_PATH.exists():
        files.append(PLAN_CONFIG_PATH.name)

    add = _run_git("add", *files)
    if add.returncode != 0:
        print(f"WARNING: 'git add' failed: {add.stderr.strip()}", file=sys.stderr)
        return

    if _run_git("diff", "--cached", "--quiet", "--", *files).returncode == 0:
        print("No changes -- nothing to commit.")
        return

    commit = _run_git(
        "commit", "-m", f"Refresh dashboard - {datetime.now().isoformat(timespec='minutes')}"
    )
    if commit.returncode != 0:
        print(f"WARNING: git commit failed: {commit.stderr.strip()}", file=sys.stderr)
        return

    push = _run_git("push", "origin", "HEAD")
    if push.returncode != 0:
        print(f"WARNING: git push failed: {push.stderr.strip()}", file=sys.stderr)
        return

    print("Pushed updated files to origin.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-push", action="store_true",
        help="Build index.html only; skip the git commit/push step.",
    )
    parser.add_argument(
        "--regen-plan", action="store_true",
        help="Force-regenerate training_plan_config.json from current fitness/mileage "
             "(overwrites any manual edits to the plan).",
    )
    args = parser.parse_args()
    PUSH_ENABLED = not args.no_push
    REGEN_PLAN = args.regen_plan
    main()
