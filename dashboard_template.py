"""HTML/CSS/JS template for dashboard.py. Kept in its own module so dashboard.py
stays readable. TEMPLATE.replace("__DASHBOARD_DATA__", json.dumps(data)) (plus the
__OG_*__ meta-tag placeholders) produces the final self-contained index.html."""

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Training Dashboard</title>
<meta property="og:type" content="website">
<meta property="og:title" content="__OG_TITLE__">
<meta property="og:description" content="__OG_DESC__">
<meta property="og:image" content="__OG_IMAGE_URL__">
<meta property="og:url" content="__OG_URL__">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="__OG_TITLE__">
<meta name="twitter:description" content="__OG_DESC__">
<meta name="twitter:image" content="__OG_IMAGE_URL__">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<style>
:root {
  color-scheme: light;
  --surface-1:      #fcfcfb;
  --page:           #f9f9f7;
  --text-primary:   #0b0b0b;
  --text-secondary: #52514e;
  --text-muted:     #898781;
  --grid:           #e1e0d9;
  --baseline:       #c3c2b7;
  --border:         rgba(11,11,11,0.10);
  --series-1: #2a78d6; /* blue */
  --series-2: #eb6834; /* orange */
  --series-3: #1baf7a; /* aqua */
  --series-7: #4a3aa7; /* violet */
  --series-8: #e34948; /* red */
  --good:     #0ca30c;
  --warning:  #fab219;
  --critical: #d03b3b;
  --shadow-card: 0 1px 2px rgba(11,11,11,0.05), 0 4px 14px rgba(11,11,11,0.045);
  --sp-1: 8px; --sp-2: 12px; --sp-3: 16px; --sp-4: 20px;
  --sp-5: 24px; --sp-6: 32px; --sp-7: 40px; --sp-8: 48px;
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) {
    color-scheme: dark;
    --surface-1:      #1a1a19;
    --page:           #0d0d0d;
    --text-primary:   #ffffff;
    --text-secondary: #c3c2b7;
    --text-muted:     #898781;
    --grid:           #2c2c2a;
    --baseline:       #383835;
    --border:         rgba(255,255,255,0.10);
    --series-1: #3987e5;
    --series-2: #d95926;
    --series-3: #199e70;
    --series-7: #9085e9;
    --series-8: #e66767;
    --shadow-card: 0 1px 2px rgba(0,0,0,0.32), 0 4px 16px rgba(0,0,0,0.28);
  }
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--page);
  color: var(--text-primary);
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  font-size: 14px;
  line-height: 1.45;
}
.wrap { max-width: 1180px; margin: 0 auto; padding: var(--sp-5) 20px 60px; }

/* sticky top nav */
.topnav {
  position: sticky; top: 0; z-index: 20;
  background: color-mix(in srgb, var(--page) 86%, transparent);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
}
.topnav-inner {
  max-width: 1180px; margin: 0 auto; padding: 12px 20px;
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
}
.brand { font-weight: 700; font-size: 14px; letter-spacing: -0.01em; }
.topnav-links { display: flex; gap: 2px; }
.topnav-links a {
  color: var(--text-secondary); text-decoration: none; font-size: 12.5px;
  font-weight: 500; padding: 7px 12px; border-radius: 8px; transition: background 0.12s, color 0.12s;
}
.topnav-links a:hover { color: var(--text-primary); background: rgba(127,127,127,0.10); }
@media (max-width: 700px) { .topnav-links { display: none; } }

/* header */
header.hero {
  background: var(--surface-1);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-card);
  border-radius: 16px;
  padding: var(--sp-5) var(--sp-6);
  margin: var(--sp-5) 0 var(--sp-6);
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--sp-4);
}
.hero-race { min-width: 240px; }
.hero-race .name { font-size: 15px; color: var(--text-secondary); font-weight: 600; }
.hero-race .date { font-size: 13px; color: var(--text-muted); margin-top: 2px; }
.hero-countdown { display: flex; align-items: baseline; gap: 10px; }
.hero-countdown .num { font-size: 56px; font-weight: 800; letter-spacing: -0.03em; }
.hero-countdown .unit { font-size: 14px; color: var(--text-secondary); }
.hero-sub { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.unit-toggle {
  display: inline-flex; border: 1px solid var(--border); border-radius: 999px; overflow: hidden;
}
.unit-toggle button {
  border: 0; background: transparent; color: var(--text-secondary);
  padding: 6px 14px; font-size: 12px; cursor: pointer; font-family: inherit;
}
.unit-toggle button.active { background: var(--series-1); color: white; }

/* page sections */
.section { margin-bottom: var(--sp-7); }
.section-head {
  position: relative;
  display: flex; align-items: center; gap: 10px; margin-bottom: var(--sp-4);
  padding: 2px 0 var(--sp-2) 16px; border-bottom: 1px solid var(--border);
}
.section-head::before {
  content: ""; position: absolute; left: 0; top: 2px; bottom: 12px;
  width: 3px; border-radius: 2px; background: var(--accent, var(--text-muted));
}
.section-head.acc-fitness  { --accent: var(--series-1); }
.section-head.acc-plan     { --accent: var(--series-7); }
.section-head.acc-effort   { --accent: var(--series-2); }
.section-head.acc-wellness { --accent: var(--series-3); }
.section-head.acc-runs     { --accent: var(--text-muted); }
.section-head h2 { margin: 0; font-size: 18px; letter-spacing: -0.01em; font-weight: 700; }
.section-head .section-note { font-size: 12px; color: var(--text-muted); }

/* stat tiles */
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: var(--sp-3); margin-bottom: var(--sp-4); }
.tile {
  background: var(--surface-1); border: 1px solid var(--border); box-shadow: var(--shadow-card);
  border-radius: 14px; padding: var(--sp-3) var(--sp-4);
}
.tile .label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
.tile .value { font-size: 30px; font-weight: 800; margin-top: 6px; letter-spacing: -0.02em; }
.tile .value .u { font-size: 12px; font-weight: 400; color: var(--text-secondary); margin-left: 3px; }
/* Fixed-height wrapper is required: Chart.js (responsive + maintainAspectRatio:
   false) sizes the canvas from its immediate parent's box via ResizeObserver,
   not from CSS on the canvas itself, so the canvas needs a positioned parent
   with a real height rather than a height rule on the canvas element. */
.spark-wrap { position: relative; height: 40px; margin-top: 10px; }
.spark-wrap canvas { width: 100% !important; height: 100% !important; }

/* predictions */
.predictions { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: var(--sp-3); margin-bottom: var(--sp-4); }
.pred-tile { background: var(--surface-1); border: 1px solid var(--border); box-shadow: var(--shadow-card); border-radius: 14px; padding: var(--sp-3) var(--sp-4); }
.pred-tile .dist { font-size: 12px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; }
.pred-tile .time { font-size: 24px; font-weight: 800; margin-top: 4px; letter-spacing: -0.02em; }
.pred-tile .pb { font-size: 11px; color: var(--text-muted); margin-top: 5px; }

/* cards */
.card {
  background: var(--surface-1); border: 1px solid var(--border); box-shadow: var(--shadow-card);
  border-radius: 16px; padding: var(--sp-4) var(--sp-5); margin-bottom: var(--sp-3);
}
.card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: var(--sp-2); }
.card-head h3 { margin: 0; font-size: 14px; font-weight: 700; }
.card-note { font-size: 12px; color: var(--text-muted); margin-top: 3px; max-width: 62ch; }
.card-grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: var(--sp-3); }
@media (max-width: 860px) { .card-grid2 { grid-template-columns: 1fr; } }
.chart-box { position: relative; height: 260px; }
.chart-box.small { height: 180px; }

.table-btn {
  border: 1px solid var(--border); background: transparent; color: var(--text-secondary);
  border-radius: 8px; padding: 4px 10px; font-size: 11px; cursor: pointer; font-family: inherit; white-space: nowrap;
}
.table-btn:hover { color: var(--text-primary); }

table.data-table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 10px; display: none; }
table.data-table.visible { display: table; }
table.data-table th {
  text-align: left; color: var(--text-muted); font-weight: 500; font-size: 11px;
  text-transform: uppercase; letter-spacing: 0.03em; padding: 6px 8px; border-bottom: 1px solid var(--grid);
}
table.data-table td { padding: 6px 8px; border-bottom: 1px solid var(--grid); font-variant-numeric: tabular-nums; }
table.data-table tbody tr:hover { background: rgba(127,127,127,0.06); }
.table-wrap { overflow-x: auto; }

.badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; }
.badge-easy { background: color-mix(in srgb, var(--good) 18%, transparent); color: var(--good); }
.badge-moderate { background: color-mix(in srgb, var(--warning) 22%, transparent); color: #8a5a00; }
.badge-hard { background: color-mix(in srgb, var(--critical) 18%, transparent); color: var(--critical); }
.badge-unknown { background: rgba(127,127,127,0.15); color: var(--text-muted); }
/* plan phases are an identity, not a good/bad status -- distinct badge set,
   reusing the categorical chart slots rather than the good/warning/critical ramp */
.badge-phase-base  { background: color-mix(in srgb, var(--series-1) 16%, transparent); color: var(--series-1); }
.badge-phase-build { background: color-mix(in srgb, var(--series-2) 16%, transparent); color: var(--series-2); }
.badge-phase-peak  { background: color-mix(in srgb, var(--series-7) 16%, transparent); color: var(--series-7); }
.badge-phase-taper { background: color-mix(in srgb, var(--series-3) 16%, transparent); color: var(--series-3); }
@media (prefers-color-scheme: dark) {
  .badge-moderate { color: var(--warning); }
}

.note-banner {
  background: color-mix(in srgb, var(--warning) 12%, var(--surface-1));
  border: 1px solid color-mix(in srgb, var(--warning) 35%, var(--border));
  border-radius: 12px; padding: 12px 16px; font-size: 12.5px; color: var(--text-secondary);
  margin-bottom: var(--sp-4);
}
.note-banner.small { padding: 8px 14px; font-size: 11.5px; margin-bottom: var(--sp-3); }
.legend-row { display: flex; gap: 14px; flex-wrap: wrap; font-size: 11px; color: var(--text-secondary); margin-top: 8px; }
.legend-row .dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 5px; vertical-align: middle; }
.footer-note { font-size: 11px; color: var(--text-muted); text-align: center; margin-top: var(--sp-6); }

/* intensity-minutes meter */
.meter-track {
  position: relative; height: 14px; border-radius: 999px; overflow: hidden;
  background: color-mix(in srgb, var(--series-1) 12%, var(--surface-1));
  border: 1px solid var(--border);
}
.meter-fill { position: absolute; top: 0; bottom: 0; }
.meter-fill.moderate { background: color-mix(in srgb, var(--series-1) 45%, var(--surface-1)); }
.meter-fill.vigorous { background: var(--series-1); }
.meter-goal-tick { position: absolute; top: -3px; bottom: -3px; width: 2px; background: var(--text-primary); opacity: 0.55; }
.meter-value { font-size: 12.5px; color: var(--text-secondary); margin-top: var(--sp-2); }
.meter-value b { color: var(--text-primary); font-weight: 800; font-size: 15px; }
.fitness-age-value { font-size: 30px; font-weight: 800; letter-spacing: -0.02em; }
.fitness-age-value .u { font-size: 12px; font-weight: 400; color: var(--text-secondary); margin-left: 3px; }
</style>
</head>
<body>

<nav class="topnav">
  <div class="topnav-inner">
    <span class="brand">Training Dashboard</span>
    <div class="topnav-links">
      <a href="#section-fitness">Fitness</a>
      <a href="#section-plan">Plan</a>
      <a href="#section-effort">Effort</a>
      <a href="#section-wellness">Wellness</a>
      <a href="#section-runs">Runs</a>
    </div>
  </div>
</nav>

<div class="wrap">

  <header class="hero">
    <div class="hero-race">
      <div class="name" id="race-name"></div>
      <div class="date" id="race-date"></div>
    </div>
    <div class="hero-countdown">
      <span class="num" id="days-left"></span>
      <span class="unit">days<br><span id="weeks-left"></span> weeks</span>
    </div>
    <div class="unit-toggle" role="group" aria-label="Units">
      <button data-unit="km" id="unit-km">km</button>
      <button data-unit="mi" id="unit-mi">mi</button>
    </div>
  </header>

  <div id="missing-data-note" class="note-banner"></div>

  <section class="section" id="section-overview">
    <div class="predictions" id="predictions-row"></div>
    <div class="tiles" id="stat-tiles"></div>
  </section>

  <section class="section" id="section-fitness">
    <div class="section-head acc-fitness"><h2>Fitness &amp; training load</h2></div>
    <div class="card">
      <div class="card-head">
        <div>
          <h3>Fitness / Fatigue / Form (estimated)</h3>
          <div class="card-note">CTL (fitness, 42-day), ATL (fatigue, 7-day) and TSB (form = CTL &minus; ATL), computed from a heart-rate/duration training-load estimate &mdash; not Garmin's official Firstbeat training status, which isn't available on your devices.</div>
        </div>
        <button class="table-btn" data-toggle="table-load">Table</button>
      </div>
      <div class="chart-box"><canvas id="chart-load"></canvas></div>
      <div class="table-wrap"><table class="data-table" id="table-load"></table></div>
    </div>
    <div class="card">
      <div class="card-head">
        <div>
          <h3>Weekly mileage</h3>
          <div class="card-note">Running distance per week, last <span id="mileage-weeks-n"></span> weeks, with a linear trend line.</div>
        </div>
        <button class="table-btn" data-toggle="table-mileage">Table</button>
      </div>
      <div class="chart-box"><canvas id="chart-mileage"></canvas></div>
      <div class="table-wrap"><table class="data-table" id="table-mileage"></table></div>
    </div>
  </section>

  <section class="section" id="section-plan">
    <div class="section-head acc-plan"><h2>Plan</h2><span class="section-note">Base &rarr; build &rarr; peak &rarr; taper, generated from your recent mileage &amp; fitness</span></div>
    <div class="card">
      <div class="card-head">
        <div>
          <h3>Target vs. actual weekly volume</h3>
          <div class="card-note">Generated once from your fitness/mileage trend, then kept fixed &mdash; edit <code>training_plan_config.json</code> by hand and it won't be overwritten on refresh (run with <code>--regen-plan</code> to force a fresh plan).</div>
        </div>
      </div>
      <div class="chart-box"><canvas id="chart-plan"></canvas></div>
    </div>
    <div class="card">
      <div class="table-wrap"><table class="data-table visible" id="table-plan"></table></div>
    </div>
  </section>

  <section class="section" id="section-effort">
    <div class="section-head acc-effort"><h2>Effort</h2></div>
    <div class="card">
      <div class="card-head">
        <div>
          <h3>Easy vs. workout volume</h3>
          <div class="card-note">Share of running distance in the window, graded by time spent above your estimated threshold heart rate (<span id="threshold-hr"></span> bpm, <span id="threshold-source"></span>).</div>
        </div>
      </div>
      <div id="effort-split" class="legend-row"></div>
    </div>
    <div class="card-grid2">
      <div class="card">
        <div class="card-head">
          <div><h3>Pace vs. heart rate</h3><div class="card-note">Every run in the window.</div></div>
          <button class="table-btn" data-toggle="table-scatter">Table</button>
        </div>
        <div class="chart-box"><canvas id="chart-scatter"></canvas></div>
        <div class="table-wrap"><table class="data-table" id="table-scatter"></table></div>
      </div>
      <div class="card">
        <div class="card-head">
          <div><h3>Easy-run heart rate over time</h3><div class="card-note">Are your easy days getting easier at the same effort?</div></div>
          <button class="table-btn" data-toggle="table-easyhr">Table</button>
        </div>
        <div class="chart-box"><canvas id="chart-easyhr"></canvas></div>
        <div class="table-wrap"><table class="data-table" id="table-easyhr"></table></div>
      </div>
    </div>
    <div class="card">
      <div class="card-head">
        <div>
          <h3>Aerobic decoupling on long runs</h3>
          <div class="card-note">Runs &ge;8&nbsp;km or &ge;40&nbsp;min (excluding interval/threshold sessions): % drop in pace-per-heart-rate efficiency, first half vs. second half. Under ~5% is generally considered well-controlled; above ~10% suggests fading form or heat/fatigue.</div>
        </div>
        <button class="table-btn" data-toggle="table-decoupling">Table</button>
      </div>
      <div class="chart-box"><canvas id="chart-decoupling"></canvas></div>
      <div class="table-wrap"><table class="data-table" id="table-decoupling"></table></div>
    </div>
  </section>

  <section class="section" id="section-wellness">
    <div class="section-head acc-wellness"><h2>Wellness</h2></div>
    <div class="note-banner small" id="floors-note" style="display:none;"></div>
    <div class="card">
      <div class="card-head">
        <div><h3>Steps</h3><div class="card-note">Daily step count.</div></div>
        <button class="table-btn" data-toggle="table-steps">Table</button>
      </div>
      <div class="chart-box small"><canvas id="chart-steps"></canvas></div>
      <div class="table-wrap"><table class="data-table" id="table-steps"></table></div>
    </div>
    <div class="card-grid2">
      <div class="card">
        <div class="card-head"><div><h3>Fitness Age</h3><div class="card-note">Garmin's estimate vs. your chronological age &mdash; a real Garmin metric, not derived.</div></div></div>
        <div id="fitness-age-block"></div>
      </div>
      <div class="card">
        <div class="card-head"><div><h3>Intensity minutes</h3><div class="card-note">Moderate + vigorous minutes this week vs. your weekly goal.</div></div></div>
        <div id="intensity-meter"></div>
      </div>
    </div>
    <div class="card-grid2">
      <div class="card">
        <div class="card-head">
          <div><h3>Resting heart rate</h3><div class="card-note">Daily value with 7-day rolling average.</div></div>
          <button class="table-btn" data-toggle="table-rhr">Table</button>
        </div>
        <div class="chart-box"><canvas id="chart-rhr"></canvas></div>
        <div class="table-wrap"><table class="data-table" id="table-rhr"></table></div>
      </div>
      <div class="card">
        <div class="card-head">
          <div><h3>Body Battery</h3><div class="card-note">Daily charged vs. drained.</div></div>
          <button class="table-btn" data-toggle="table-battery">Table</button>
        </div>
        <div class="chart-box"><canvas id="chart-battery"></canvas></div>
        <div class="table-wrap"><table class="data-table" id="table-battery"></table></div>
      </div>
    </div>
    <div class="card-grid2">
      <div class="card">
        <div class="card-head">
          <div><h3>Stress</h3><div class="card-note">Daily average and peak stress score.</div></div>
          <button class="table-btn" data-toggle="table-stress">Table</button>
        </div>
        <div class="chart-box"><canvas id="chart-stress"></canvas></div>
        <div class="table-wrap"><table class="data-table" id="table-stress"></table></div>
      </div>
      <div class="card">
        <div class="card-head">
          <div><h3>VO&sub2; max</h3><div class="card-note">Garmin's FirstBeat estimate. Updates infrequently &mdash; expect a step chart, not a smooth curve.</div></div>
          <button class="table-btn" data-toggle="table-vo2">Table</button>
        </div>
        <div class="chart-box"><canvas id="chart-vo2"></canvas></div>
        <div class="table-wrap"><table class="data-table" id="table-vo2"></table></div>
      </div>
    </div>
  </section>

  <section class="section" id="section-runs">
    <div class="section-head acc-runs"><h2>Recent runs</h2><span class="section-note">Last <span id="runs-days-n"></span> days</span></div>
    <div class="card">
      <div class="table-wrap"><table class="data-table visible" id="table-runs"></table></div>
    </div>
  </section>

  <div class="footer-note" id="generated-at"></div>
</div>

<script>
const DATA = __DASHBOARD_DATA__;
let UNIT = "km";
const charts = {};

/* ---------- formatting helpers ---------- */
function fmtDist(km) {
  if (km === null || km === undefined) return "–";
  const v = UNIT === "km" ? km : km * 0.621371;
  return v.toFixed(v < 10 ? 2 : 1) + " " + UNIT;
}
function fmtPaceSecPerKm(spk) {
  if (!spk) return "–";
  const secPerUnit = UNIT === "km" ? spk : spk * 1.609344;
  const m = Math.floor(secPerUnit / 60);
  const s = Math.round(secPerUnit % 60);
  return m + ":" + String(s).padStart(2, "0") + "/" + UNIT;
}
function fmtDuration(sec) {
  if (!sec) return "–";
  const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = Math.round(sec % 60);
  return h > 0 ? `${h}:${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}` : `${m}:${String(s).padStart(2,"0")}`;
}
function fmtTimeShort(sec) {
  if (sec === null || sec === undefined) return "–";
  const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = Math.round(sec % 60);
  return h > 0 ? `${h}:${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}` : `${m}:${String(s).padStart(2,"0")}`;
}
function fmtDate(d) {
  if (!d) return "–";
  const dt = new Date(d + "T00:00:00");
  return dt.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}
function css(varName) { return getComputedStyle(document.documentElement).getPropertyValue(varName).trim(); }
function effortBadge(effort, hardPct) {
  const cls = { easy: "badge-easy", moderate: "badge-moderate", hard: "badge-hard" }[effort] || "badge-unknown";
  const label = effort ? effort.charAt(0).toUpperCase() + effort.slice(1) : "Unknown";
  return `<span class="badge ${cls}">${label}</span>`;
}
function phaseBadge(phase) {
  const cls = { base: "badge-phase-base", build: "badge-phase-build", peak: "badge-phase-peak", taper: "badge-phase-taper" }[phase] || "badge-unknown";
  const label = phase ? phase.charAt(0).toUpperCase() + phase.slice(1) : "–";
  return `<span class="badge ${cls}">${label}</span>`;
}
function statusBadge(status) {
  const cls = { hit: "badge-easy", missed: "badge-hard", upcoming: "badge-unknown", no_data: "badge-unknown" }[status] || "badge-unknown";
  const label = { hit: "Hit", missed: "Missed", upcoming: "Upcoming", no_data: "No data" }[status] || status;
  return `<span class="badge ${cls}">${label}</span>`;
}

/* ---------- generic chart-card table toggle ---------- */
document.querySelectorAll(".table-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const t = document.getElementById(btn.dataset.toggle);
    if (t) t.classList.toggle("visible");
  });
});

function buildTable(el, columns, rows) {
  el.innerHTML = "";
  const thead = document.createElement("thead");
  const trh = document.createElement("tr");
  columns.forEach(c => { const th = document.createElement("th"); th.textContent = c.label; trh.appendChild(th); });
  thead.appendChild(trh);
  const tbody = document.createElement("tbody");
  rows.forEach(row => {
    const tr = document.createElement("tr");
    columns.forEach(c => { const td = document.createElement("td"); td.innerHTML = c.render(row); tr.appendChild(td); });
    tbody.appendChild(tr);
  });
  el.appendChild(thead);
  el.appendChild(tbody);
}

function destroyChart(id) { if (charts[id]) { charts[id].destroy(); delete charts[id]; } }

function baseGridOptions() {
  return {
    grid: { color: css("--grid"), drawTicks: false },
    ticks: { color: css("--text-muted"), font: { size: 11 } },
    border: { color: css("--baseline") },
  };
}

/* ---------- header / countdown ---------- */
function renderHeader() {
  document.getElementById("race-name").textContent = DATA.race.name;
  const rd = new Date(DATA.race.date + "T00:00:00");
  document.getElementById("race-date").textContent = rd.toLocaleDateString(undefined, { weekday: "long", year: "numeric", month: "long", day: "numeric" });
  document.getElementById("days-left").textContent = DATA.race.days_left;
  document.getElementById("weeks-left").textContent = DATA.race.weeks_left;
  document.getElementById("generated-at").textContent = "Generated " + new Date(DATA.generated_at).toLocaleString();
  document.getElementById("missing-data-note").textContent = DATA.missing_data_note;
  document.getElementById("mileage-weeks-n").textContent = DATA.weekly_mileage.length;
  document.getElementById("runs-days-n").textContent = DATA.recent_runs_days;
  document.getElementById("threshold-hr").textContent = DATA.profile.threshold_hr;
  document.getElementById("threshold-source").textContent = DATA.profile.threshold_source;
}

/* ---------- predictions ---------- */
function renderPredictions() {
  const el = document.getElementById("predictions-row");
  el.innerHTML = "";
  const cur = DATA.predictions.current;
  const defs = [
    ["5K", cur && cur["5k_s"], "5K"],
    ["10K", cur && cur["10k_s"], "10K"],
    ["Half Marathon", cur && cur["half_s"], "Half Marathon"],
    ["Marathon", cur && cur["marathon_s"], "Marathon"],
  ];
  defs.forEach(([label, secs, pbKey]) => {
    const pb = DATA.personal_bests[pbKey];
    const div = document.createElement("div");
    div.className = "pred-tile";
    div.innerHTML = `<div class="dist">${label} predicted</div>
      <div class="time">${secs ? fmtTimeShort(secs) : "–"}</div>
      <div class="pb">PB: ${pb ? fmtTimeShort(pb) : "no PB yet"}</div>`;
    el.appendChild(div);
  });
}

/* ---------- stat tiles ---------- */
function sparkline(canvasId, series, color) {
  const ctx = document.getElementById(canvasId);
  if (!ctx || !series.length) return;
  new Chart(ctx, {
    type: "line",
    data: { labels: series.map((_, i) => i), datasets: [{ data: series, borderColor: color, borderWidth: 1.5, pointRadius: 0, tension: 0.3, fill: false }] },
    options: {
      responsive: true, maintainAspectRatio: false, animation: false,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      scales: { x: { display: false }, y: { display: false } },
      elements: { line: { borderJoinStyle: "round" } },
    },
  });
}
function renderStatTiles() {
  const el = document.getElementById("stat-tiles");
  const t = DATA.stat_tiles;
  const tiles = [
    { label: "Fitness (CTL, est.)", value: t.fitness, unit: "", spark: DATA.training_load.map(p => p.ctl), color: "var(--series-1)", id: "spark-fitness" },
    { label: "Fatigue (ATL, est.)", value: t.fatigue, unit: "", spark: DATA.training_load.map(p => p.atl), color: "var(--series-2)", id: "spark-fatigue" },
    { label: "Form (TSB, est.)", value: t.form, unit: "", spark: DATA.training_load.map(p => p.tsb), color: "var(--series-7)", id: "spark-form" },
    { label: "7-day volume", value: null, unit: "", spark: DATA.weekly_mileage.map(w => w.km), color: "var(--series-3)", id: "spark-volume", custom: fmtDist(t.week_km) },
    { label: "VO₂ max", value: t.vo2max ?? "–", unit: "", spark: DATA.vo2max.trend.map(p => p.value), color: "var(--series-1)", id: "spark-vo2" },
    { label: "Resting HR", value: t.resting_hr ?? "–", unit: "bpm", spark: DATA.wellness.rhr.map(p => p.value), color: "var(--series-2)", id: "spark-rhr" },
    { label: "Avg stress", value: t.avg_stress ?? "–", unit: "", spark: DATA.wellness.stress.map(p => p.avg), color: "var(--series-8)", id: "spark-stress" },
  ];
  el.innerHTML = "";
  tiles.forEach(tile => {
    const div = document.createElement("div");
    div.className = "tile";
    div.innerHTML = `<div class="label">${tile.label}</div>
      <div class="value">${tile.custom ?? tile.value}${tile.unit ? `<span class="u">${tile.unit}</span>` : ""}</div>
      <div class="spark-wrap"><canvas id="${tile.id}"></canvas></div>`;
    el.appendChild(div);
  });
  tiles.forEach(tile => sparkline(tile.id, tile.spark.filter(v => v !== null && v !== undefined), tile.color));
}

/* ---------- fitness tab ---------- */
function renderLoadChart() {
  destroyChart("load");
  const rows = DATA.training_load;
  const grid = baseGridOptions();
  charts.load = new Chart(document.getElementById("chart-load"), {
    type: "line",
    data: {
      labels: rows.map(r => r.date),
      datasets: [
        { label: "Fitness (CTL)", data: rows.map(r => r.ctl), borderColor: css("--series-1"), backgroundColor: css("--series-1"), borderWidth: 2, pointRadius: 0, tension: 0.25 },
        { label: "Fatigue (ATL)", data: rows.map(r => r.atl), borderColor: css("--series-2"), backgroundColor: css("--series-2"), borderWidth: 2, pointRadius: 0, tension: 0.25 },
        { label: "Form (TSB)", data: rows.map(r => r.tsb), borderColor: css("--series-7"), backgroundColor: css("--series-7"), borderWidth: 2, pointRadius: 0, tension: 0.25, borderDash: [4, 3] },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: { legend: { labels: { color: css("--text-secondary"), boxWidth: 10, font: { size: 11 } } } },
      scales: {
        x: { ticks: { ...grid.ticks, maxTicksLimit: 10, callback: (v, i) => fmtDate(rows[i]?.date) }, grid: { display: false }, border: grid.border },
        y: { ticks: grid.ticks, grid: grid.grid, border: grid.border },
      },
    },
  });
  buildTable(document.getElementById("table-load"),
    [{ label: "Date", render: r => fmtDate(r.date) }, { label: "Fitness", render: r => r.ctl }, { label: "Fatigue", render: r => r.atl }, { label: "Form", render: r => r.tsb }],
    rows);
}

function renderMileageChart() {
  destroyChart("mileage");
  const rows = DATA.weekly_mileage;
  const grid = baseGridOptions();
  const dist = rows.map(r => UNIT === "km" ? r.km : r.km * 0.621371);
  const trend = rows.map(r => UNIT === "km" ? r.trend_km : r.trend_km * 0.621371);
  charts.mileage = new Chart(document.getElementById("chart-mileage"), {
    data: {
      labels: rows.map(r => r.week_start),
      datasets: [
        { type: "bar", label: "Weekly " + UNIT, data: dist, backgroundColor: css("--series-1"), borderRadius: 4, maxBarThickness: 28 },
        { type: "line", label: "Trend", data: trend, borderColor: css("--series-2"), borderWidth: 2, pointRadius: 0, tension: 0.15 },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { labels: { color: css("--text-secondary"), boxWidth: 10, font: { size: 11 } } } },
      scales: {
        x: { ticks: { ...grid.ticks, callback: (v, i) => fmtDate(rows[i]?.week_start) }, grid: { display: false }, border: grid.border },
        y: { ticks: grid.ticks, grid: grid.grid, border: grid.border, title: { display: true, text: UNIT, color: css("--text-muted") } },
      },
    },
  });
  buildTable(document.getElementById("table-mileage"),
    [{ label: "Week of", render: r => fmtDate(r.week_start) }, { label: "Distance", render: r => fmtDist(r.km) }, { label: "Runs", render: r => r.runs }],
    rows);
}

/* ---------- plan section ---------- */
function renderPlanChart() {
  destroyChart("plan");
  const rows = DATA.plan.weeks;
  const grid = baseGridOptions();
  const target = rows.map(r => UNIT === "km" ? r.target_km : r.target_km * 0.621371);
  const actual = rows.map(r => (r.actual_km === null || r.actual_km === undefined) ? null : (UNIT === "km" ? r.actual_km : r.actual_km * 0.621371));
  charts.plan = new Chart(document.getElementById("chart-plan"), {
    data: {
      labels: rows.map(r => "W" + r.week_num),
      datasets: [
        { type: "bar", label: "Target " + UNIT, data: target, backgroundColor: css("--series-7"), borderRadius: 4, maxBarThickness: 22 },
        { type: "line", label: "Actual " + UNIT, data: actual, borderColor: css("--series-2"), backgroundColor: css("--series-2"), pointRadius: 4, borderWidth: 2, spanGaps: false },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { labels: { color: css("--text-secondary"), boxWidth: 10, font: { size: 11 } } } },
      scales: {
        x: { ticks: { ...grid.ticks, maxTicksLimit: 14 }, grid: { display: false }, border: grid.border },
        y: { ticks: grid.ticks, grid: grid.grid, border: grid.border, title: { display: true, text: UNIT, color: css("--text-muted") } },
      },
    },
  });
}

function renderPlanTable() {
  buildTable(document.getElementById("table-plan"),
    [
      { label: "Week", render: r => r.week_num },
      { label: "Week of", render: r => fmtDate(r.week_start) },
      { label: "Phase", render: r => phaseBadge(r.phase) },
      { label: "Target", render: r => fmtDist(r.target_km) },
      { label: "Actual", render: r => (r.actual_km === null || r.actual_km === undefined) ? "–" : fmtDist(r.actual_km) },
      { label: "Status", render: r => statusBadge(r.status) },
      { label: "Key workout", render: r => r.key_workout },
    ],
    DATA.plan.weeks);
}

/* ---------- effort tab ---------- */
function renderEffortSplit() {
  const el = document.getElementById("effort-split");
  const runs = DATA.runs;
  const totals = { easy: 0, moderate: 0, hard: 0, unknown: 0 };
  runs.forEach(r => { totals[r.effort || "unknown"] += r.distance_km; });
  const total = Object.values(totals).reduce((a, b) => a + b, 0) || 1;
  const colors = { easy: "var(--good)", moderate: "var(--warning)", hard: "var(--critical)", unknown: "var(--text-muted)" };
  el.innerHTML = "";
  ["easy", "moderate", "hard"].forEach(k => {
    const pct = (totals[k] / total * 100).toFixed(0);
    const span = document.createElement("span");
    span.innerHTML = `<span class="dot" style="background:${colors[k]}"></span>${k.charAt(0).toUpperCase()+k.slice(1)}: ${pct}% (${fmtDist(totals[k])})`;
    el.appendChild(span);
  });
}

function renderScatterChart() {
  destroyChart("scatter");
  const runs = DATA.runs.filter(r => r.avg_hr && r.pace_s_per_km);
  const grid = baseGridOptions();
  const colors = { easy: css("--good"), moderate: css("--warning"), hard: css("--critical"), unknown: css("--text-muted") };
  const byEffort = { easy: [], moderate: [], hard: [], unknown: [] };
  runs.forEach(r => {
    const paceUnit = UNIT === "km" ? r.pace_s_per_km : r.pace_s_per_km * 1.609344;
    (byEffort[r.effort] || byEffort.unknown).push({ x: r.avg_hr, y: paceUnit / 60, run: r });
  });
  charts.scatter = new Chart(document.getElementById("chart-scatter"), {
    type: "scatter",
    data: {
      datasets: Object.entries(byEffort).filter(([, v]) => v.length).map(([k, v]) => ({
        label: k.charAt(0).toUpperCase() + k.slice(1), data: v, backgroundColor: colors[k], pointRadius: 4,
      })),
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: css("--text-secondary"), boxWidth: 10, font: { size: 11 } } },
        tooltip: { callbacks: { label: (ctx) => `${ctx.raw.run.date}: ${fmtPaceSecPerKm(ctx.raw.run.pace_s_per_km)} @ ${ctx.raw.x} bpm` } },
      },
      scales: {
        x: { title: { display: true, text: "Avg HR (bpm)", color: css("--text-muted") }, ticks: grid.ticks, grid: grid.grid, border: grid.border },
        y: { reverse: true, title: { display: true, text: "Pace (min/" + UNIT + ")", color: css("--text-muted") }, ticks: grid.ticks, grid: grid.grid, border: grid.border },
      },
    },
  });
  buildTable(document.getElementById("table-scatter"),
    [{ label: "Date", render: r => fmtDate(r.date) }, { label: "Effort", render: r => effortBadge(r.effort) }, { label: "Pace", render: r => fmtPaceSecPerKm(r.pace_s_per_km) }, { label: "Avg HR", render: r => r.avg_hr ?? "–" }],
    runs);
}

function renderEasyHrChart() {
  destroyChart("easyhr");
  const runs = DATA.runs.filter(r => r.effort === "easy" && r.avg_hr).slice().sort((a, b) => a.date.localeCompare(b.date));
  const grid = baseGridOptions();
  charts.easyhr = new Chart(document.getElementById("chart-easyhr"), {
    type: "line",
    data: { labels: runs.map(r => r.date), datasets: [{ label: "Avg HR (easy runs)", data: runs.map(r => r.avg_hr), borderColor: css("--good"), backgroundColor: css("--good"), pointRadius: 3, borderWidth: 2, tension: 0.2 }] },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { ...grid.ticks, callback: (v, i) => fmtDate(runs[i]?.date) }, grid: { display: false }, border: grid.border },
        y: { title: { display: true, text: "bpm", color: css("--text-muted") }, ticks: grid.ticks, grid: grid.grid, border: grid.border },
      },
    },
  });
  buildTable(document.getElementById("table-easyhr"),
    [{ label: "Date", render: r => fmtDate(r.date) }, { label: "Distance", render: r => fmtDist(r.distance_km) }, { label: "Avg HR", render: r => r.avg_hr }, { label: "Pace", render: r => fmtPaceSecPerKm(r.pace_s_per_km) }],
    runs);
}

function renderDecouplingChart() {
  destroyChart("decoupling");
  const runs = DATA.runs.filter(r => r.decoupling_pct !== null && r.decoupling_pct !== undefined).slice().sort((a, b) => a.date.localeCompare(b.date));
  const grid = baseGridOptions();
  const colorFor = v => v < 5 ? css("--good") : v <= 10 ? css("--warning") : css("--critical");
  charts.decoupling = new Chart(document.getElementById("chart-decoupling"), {
    type: "bar",
    data: { labels: runs.map(r => r.date), datasets: [{ label: "Decoupling %", data: runs.map(r => r.decoupling_pct), backgroundColor: runs.map(r => colorFor(r.decoupling_pct)), borderRadius: 4, maxBarThickness: 26 }] },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: (ctx) => `${ctx.parsed.y}% decoupling` } } },
      scales: {
        x: { ticks: { ...grid.ticks, callback: (v, i) => fmtDate(runs[i]?.date) }, grid: { display: false }, border: grid.border },
        y: { title: { display: true, text: "% decoupling", color: css("--text-muted") }, ticks: grid.ticks, grid: grid.grid, border: grid.border },
      },
    },
  });
  buildTable(document.getElementById("table-decoupling"),
    [{ label: "Date", render: r => fmtDate(r.date) }, { label: "Distance", render: r => fmtDist(r.distance_km) }, { label: "Decoupling", render: r => r.decoupling_pct + "%" }],
    runs);
}

/* ---------- wellness tab ---------- */
function renderFloorsNote() {
  const el = document.getElementById("floors-note");
  if (!DATA.wellness.floors_available) {
    el.textContent = "Floors climbed isn't tracked on this device (no barometric altimeter) -- not shown.";
    el.style.display = "block";
  } else {
    el.style.display = "none";
  }
}

function renderStepsChart() {
  destroyChart("steps");
  const rows = DATA.wellness.steps;
  const grid = baseGridOptions();
  charts.steps = new Chart(document.getElementById("chart-steps"), {
    type: "bar",
    data: { labels: rows.map(r => r.date), datasets: [{ label: "Steps", data: rows.map(r => r.value), backgroundColor: css("--series-3"), borderRadius: 4, maxBarThickness: 16 }] },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { ...grid.ticks, maxTicksLimit: 10, callback: (v, i) => fmtDate(rows[i]?.date) }, grid: { display: false }, border: grid.border },
        y: { ticks: grid.ticks, grid: grid.grid, border: grid.border },
      },
    },
  });
  buildTable(document.getElementById("table-steps"),
    [{ label: "Date", render: r => fmtDate(r.date) }, { label: "Steps", render: r => r.value.toLocaleString() }],
    rows);
}

function renderIntensityMeter() {
  const el = document.getElementById("intensity-meter");
  const im = DATA.wellness.intensity_minutes;
  if (!im) {
    el.innerHTML = `<div class="card-note">No intensity-minutes data for today.</div>`;
    return;
  }
  const scale = Math.max(im.weekly_total || 0, im.week_goal || 0, 1) * 1.05;
  const modPct = Math.min(100, (im.weekly_moderate || 0) / scale * 100);
  const vigPct = Math.min(100 - modPct, (im.weekly_vigorous || 0) / scale * 100);
  const goalPct = im.week_goal ? Math.min(100, im.week_goal / scale * 100) : null;
  el.innerHTML = `
    <div class="meter-track">
      <div class="meter-fill moderate" style="width:${modPct}%"></div>
      <div class="meter-fill vigorous" style="left:${modPct}%;width:${vigPct}%"></div>
      ${goalPct !== null ? `<div class="meter-goal-tick" style="left:${goalPct}%"></div>` : ""}
    </div>
    <div class="meter-value"><b>${im.weekly_total ?? "–"}</b> / ${im.week_goal ?? "–"} min this week
      <span style="color:var(--text-muted)"> (${im.weekly_moderate ?? 0} moderate + ${im.weekly_vigorous ?? 0} vigorous)</span></div>`;
}

function renderFitnessAge() {
  const el = document.getElementById("fitness-age-block");
  const fa = DATA.wellness.fitness_age;
  if (!fa) {
    el.innerHTML = `<div class="card-note">No Fitness Age data available.</div>`;
    return;
  }
  el.innerHTML = `<div class="fitness-age-value">${fa.fitness_age}<span class="u">yrs</span></div>
    <div class="card-note" style="margin-top:8px;">Chronological age ${fa.chronological_age ?? "–"} &middot; achievable ${fa.achievable_fitness_age ?? "–"}</div>`;
}

function renderRhrChart() {
  destroyChart("rhr");
  const rows = DATA.wellness.rhr;
  const grid = baseGridOptions();
  charts.rhr = new Chart(document.getElementById("chart-rhr"), {
    type: "line",
    data: {
      labels: rows.map(r => r.date),
      datasets: [
        { label: "Daily", data: rows.map(r => r.value), borderColor: css("--series-1"), pointRadius: 2, borderWidth: 1.5, tension: 0.2 },
        { label: "7-day avg", data: rows.map(r => r.rolling7), borderColor: css("--series-2"), pointRadius: 0, borderWidth: 2, tension: 0.25 },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { labels: { color: css("--text-secondary"), boxWidth: 10, font: { size: 11 } } } },
      scales: {
        x: { ticks: { ...grid.ticks, maxTicksLimit: 8, callback: (v, i) => fmtDate(rows[i]?.date) }, grid: { display: false }, border: grid.border },
        y: { title: { display: true, text: "bpm", color: css("--text-muted") }, ticks: grid.ticks, grid: grid.grid, border: grid.border },
      },
    },
  });
  buildTable(document.getElementById("table-rhr"),
    [{ label: "Date", render: r => fmtDate(r.date) }, { label: "RHR", render: r => r.value }, { label: "7-day avg", render: r => r.rolling7 }],
    rows);
}

function renderBatteryChart() {
  destroyChart("battery");
  const rows = DATA.wellness.body_battery;
  const grid = baseGridOptions();
  charts.battery = new Chart(document.getElementById("chart-battery"), {
    type: "bar",
    data: {
      labels: rows.map(r => r.date),
      datasets: [
        { label: "Charged", data: rows.map(r => r.charged), backgroundColor: css("--series-1"), borderRadius: 3, maxBarThickness: 18 },
        { label: "Drained", data: rows.map(r => -(r.drained || 0)), backgroundColor: css("--series-8"), borderRadius: 3, maxBarThickness: 18 },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { labels: { color: css("--text-secondary"), boxWidth: 10, font: { size: 11 } } } },
      scales: {
        x: { ticks: { ...grid.ticks, maxTicksLimit: 8, callback: (v, i) => fmtDate(rows[i]?.date) }, grid: { display: false }, border: grid.border, stacked: true },
        y: { ticks: grid.ticks, grid: grid.grid, border: grid.border, stacked: true },
      },
    },
  });
  buildTable(document.getElementById("table-battery"),
    [{ label: "Date", render: r => fmtDate(r.date) }, { label: "Charged", render: r => r.charged }, { label: "Drained", render: r => r.drained }],
    rows);
}

function renderStressChart() {
  destroyChart("stress");
  const rows = DATA.wellness.stress;
  const grid = baseGridOptions();
  charts.stress = new Chart(document.getElementById("chart-stress"), {
    type: "line",
    data: {
      labels: rows.map(r => r.date),
      datasets: [
        { label: "Avg", data: rows.map(r => r.avg), borderColor: css("--series-1"), pointRadius: 0, borderWidth: 2, tension: 0.25 },
        { label: "Max", data: rows.map(r => r.max), borderColor: css("--series-8"), pointRadius: 0, borderWidth: 1.5, borderDash: [3, 3], tension: 0.25 },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { labels: { color: css("--text-secondary"), boxWidth: 10, font: { size: 11 } } } },
      scales: {
        x: { ticks: { ...grid.ticks, maxTicksLimit: 8, callback: (v, i) => fmtDate(rows[i]?.date) }, grid: { display: false }, border: grid.border },
        y: { ticks: grid.ticks, grid: grid.grid, border: grid.border },
      },
    },
  });
  buildTable(document.getElementById("table-stress"),
    [{ label: "Date", render: r => fmtDate(r.date) }, { label: "Avg", render: r => r.avg }, { label: "Max", render: r => r.max }],
    rows);
}

function renderVo2Chart() {
  destroyChart("vo2");
  const rows = DATA.vo2max.trend;
  const grid = baseGridOptions();
  charts.vo2 = new Chart(document.getElementById("chart-vo2"), {
    type: "line",
    data: { labels: rows.map(r => r.date), datasets: [{ label: "VO₂ max", data: rows.map(r => r.value), borderColor: css("--series-1"), backgroundColor: css("--series-1"), stepped: true, pointRadius: 3, borderWidth: 2 }] },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { ...grid.ticks, callback: (v, i) => fmtDate(rows[i]?.date) }, grid: { display: false }, border: grid.border },
        y: { ticks: grid.ticks, grid: grid.grid, border: grid.border },
      },
    },
  });
  buildTable(document.getElementById("table-vo2"), [{ label: "Date", render: r => fmtDate(r.date) }, { label: "VO₂ max", render: r => r.value }], rows);
}

/* ---------- runs table ---------- */
function recentRuns() {
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - DATA.recent_runs_days);
  const cutoffStr = cutoff.toISOString().slice(0, 10);
  return DATA.runs.filter(r => r.date >= cutoffStr);
}
function renderRunsTable() {
  buildTable(document.getElementById("table-runs"),
    [
      { label: "Date", render: r => fmtDate(r.date) },
      { label: "Name", render: r => r.name || "–" },
      { label: "Distance", render: r => fmtDist(r.distance_km) },
      { label: "Duration", render: r => fmtDuration(r.moving_duration_s) },
      { label: "Pace", render: r => fmtPaceSecPerKm(r.pace_s_per_km) },
      { label: "Avg HR", render: r => r.avg_hr ?? "–" },
      { label: "Max HR", render: r => r.max_hr ?? "–" },
      { label: "Effort", render: r => effortBadge(r.effort) },
    ],
    recentRuns());
  document.getElementById("table-runs").classList.add("visible");
}

/* ---------- render all + unit toggle ---------- */
function renderAll() {
  renderHeader();
  renderPredictions();
  renderStatTiles();
  renderLoadChart();
  renderMileageChart();
  renderPlanChart();
  renderPlanTable();
  renderEffortSplit();
  renderScatterChart();
  renderEasyHrChart();
  renderDecouplingChart();
  renderFloorsNote();
  renderStepsChart();
  renderIntensityMeter();
  renderFitnessAge();
  renderRhrChart();
  renderBatteryChart();
  renderStressChart();
  renderVo2Chart();
  renderRunsTable();
}

document.querySelectorAll(".unit-toggle button").forEach(btn => {
  btn.addEventListener("click", () => {
    UNIT = btn.dataset.unit;
    document.querySelectorAll(".unit-toggle button").forEach(b => b.classList.toggle("active", b === btn));
    renderMileageChart();
    renderPlanChart();
    renderPlanTable();
    renderScatterChart();
    renderRunsTable();
  });
});
document.getElementById("unit-" + UNIT).classList.add("active");

renderAll();
</script>
</body>
</html>
"""
