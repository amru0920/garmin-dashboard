"""Week-by-week training plan generator for the goal race.

Uses simple base -> build -> peak -> taper periodization, scaled off the
runner's own recent weekly mileage (not a generic marathon-plan template --
this account is training for 5K/10K, so it's speed/threshold-leaning with
modest volume growth, not marathon-length long runs).

Storage contract: the generated plan is written to training_plan_config.json
ONCE (or on an explicit --regen-plan). dashboard.py must never silently
rewrite this file on a normal run -- any manual edits the user makes (e.g.
tweaking a week's target or workout text) have to survive a refresh. Actual
mileage is merged in at render time, in memory, without touching the file.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

PHASE_WORKOUTS = {
    "base": "Easy aerobic mileage + 4-6 strides, 1 longer easy run",
    "build": "Add 1 tempo/threshold run + short VO2max intervals (e.g. 6x400m)",
    "peak": "Race-pace intervals (10K/5K pace) + 1 sharpening session",
    "taper": "Short, race-pace touches only -- cut volume, keep legs sharp",
}


def _week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())


def generate_default_plan(
    race_date: str, today: date, weekly_mileage: list[dict], ctl: float,
) -> dict:
    """Build a fresh plan config from current fitness/mileage. Only called
    when no config file exists yet, or explicitly via --regen-plan."""
    race = date.fromisoformat(race_date)
    this_week_start = _week_start(today)
    race_week_start = _week_start(race)
    total_weeks = max(1, (race_week_start - this_week_start).days // 7 + 1)

    taper_weeks = 1 if total_weeks <= 8 else 2
    peak_weeks = min(2, max(0, total_weeks - taper_weeks))
    remaining = max(0, total_weeks - taper_weeks - peak_weeks)
    build_weeks = round(remaining * 0.45)
    base_weeks = remaining - build_weeks

    phases = (
        ["base"] * base_weeks + ["build"] * build_weeks
        + ["peak"] * peak_weeks + ["taper"] * taper_weeks
    )
    phases = (phases + ["base"] * total_weeks)[:total_weeks]

    recent = [w["km"] for w in weekly_mileage[-3:] if w.get("km")]
    if recent:
        baseline_km = sum(recent) / len(recent)
    elif weekly_mileage:
        baseline_km = weekly_mileage[-1]["km"]
    else:
        baseline_km = 0.0
    baseline_km = max(baseline_km, 5.0)
    peak_cap = baseline_km * 1.6

    taper_cuts = (
        [0.4] if taper_weeks == 1
        else [0.4 + 0.2 * i / (taper_weeks - 1) for i in range(taper_weeks)]
    )

    weeks = []
    current_km = baseline_km
    peak_km = baseline_km
    taper_i = 0
    for i, phase in enumerate(phases):
        week_start = this_week_start + timedelta(weeks=i)
        if phase in ("base", "build"):
            is_cutback = (i + 1) % 4 == 0
            target = baseline_km if i == 0 else current_km * 1.065
            target = min(target, peak_cap)
            if is_cutback:
                target *= 0.75
            else:
                current_km = target
            peak_km = max(peak_km, target)
        elif phase == "peak":
            target = min(peak_km, peak_cap)
        else:  # taper
            cut = taper_cuts[min(taper_i, len(taper_cuts) - 1)]
            taper_i += 1
            target = peak_km * (1 - cut)

        weeks.append({
            "week_num": i + 1,
            "week_start": week_start.isoformat(),
            "phase": phase,
            "target_km": round(target, 1),
            "key_workout": PHASE_WORKOUTS[phase],
        })

    return {
        "race_date": race_date,
        "generated_on": today.isoformat(),
        "generated_from_ctl": round(ctl, 1),
        "baseline_weekly_km": round(baseline_km, 1),
        "weeks": weeks,
    }


def load_plan_config(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_plan_config(path: Path, config: dict) -> None:
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")


def merge_plan_with_actuals(config: dict, weekly_mileage: list[dict], today: date) -> list[dict]:
    """Join the stored plan with actual weekly mileage, without mutating config."""
    actual_by_week = {w["week_start"]: w["km"] for w in weekly_mileage}
    this_week_start = _week_start(today).isoformat()

    merged = []
    for w in config.get("weeks", []):
        actual_km = actual_by_week.get(w["week_start"])
        if w["week_start"] >= this_week_start:
            status = "upcoming"
        elif actual_km is None:
            status = "no_data"
        else:
            status = "hit" if actual_km >= 0.85 * w["target_km"] else "missed"
        merged.append({**w, "actual_km": actual_km, "status": status})
    return merged
