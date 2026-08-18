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

/* clickable tiles */
.tile, .pred-tile { cursor: pointer; transition: transform 0.12s, border-color 0.12s; }
.tile:hover, .pred-tile:hover { transform: translateY(-2px); border-color: color-mix(in srgb, var(--series-1) 45%, var(--border)); }
.tile:focus-visible, .pred-tile:focus-visible { outline: 2px solid var(--series-1); outline-offset: 2px; }
.tile .tap-hint, .pred-tile .tap-hint { font-size: 10px; color: var(--text-muted); margin-top: 8px; opacity: 0.7; }

/* metric detail modal */
.modal-overlay {
  position: fixed; inset: 0; z-index: 100; display: none;
  background: color-mix(in srgb, black 55%, transparent);
  align-items: flex-start; justify-content: center;
  padding: 48px 16px; overflow-y: auto;
}
.modal-overlay.open { display: flex; }
.modal {
  background: var(--surface-1); border: 1px solid var(--border); box-shadow: var(--shadow-card);
  border-radius: 16px; padding: var(--sp-5); max-width: 640px; width: 100%; margin: auto 0;
}
.modal-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: var(--sp-4); }
.modal-head h2 { margin: 0; font-size: 20px; font-weight: 800; letter-spacing: -0.01em; }
.modal-subtitle { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
.modal-close {
  border: 1px solid var(--border); background: transparent; color: var(--text-secondary);
  border-radius: 8px; width: 32px; height: 32px; font-size: 18px; line-height: 1; cursor: pointer;
  flex: 0 0 auto; display: flex; align-items: center; justify-content: center;
}
.modal-close:hover { color: var(--text-primary); background: rgba(127,127,127,0.10); }
.modal-chart { position: relative; height: 220px; margin-bottom: var(--sp-4); }
.modal-section { margin-bottom: var(--sp-4); }
.modal-section:last-child { margin-bottom: 0; }
.modal-section h4 {
  margin: 0 0 6px; font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--text-muted);
}
.modal-section p { font-size: 13px; color: var(--text-secondary); margin: 0 0 8px; }
.modal-section ul { margin: 0 0 8px; padding-left: 18px; }
.modal-section li { font-size: 13px; color: var(--text-secondary); margin-bottom: 4px; }
.modal-status {
  display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 11.5px;
  font-weight: 700; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.03em;
}
.modal-status.status-good { background: color-mix(in srgb, var(--good) 18%, transparent); color: var(--good); }
.modal-status.status-warn { background: color-mix(in srgb, var(--warning) 22%, transparent); color: #8a5a00; }
.modal-status.status-bad { background: color-mix(in srgb, var(--critical) 18%, transparent); color: var(--critical); }
.modal-status.status-neutral { background: rgba(127,127,127,0.15); color: var(--text-muted); }
@media (prefers-color-scheme: dark) { .modal-status.status-warn { color: var(--warning); } }

/* heart rate zones */
.hrzone-defs { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: var(--sp-2); margin-bottom: var(--sp-4); }
.hrzone-chip { border: 1px solid var(--border); border-radius: 10px; padding: 8px 10px; font-size: 11.5px; }
.hrzone-chip .hz-head { display: flex; align-items: center; gap: 6px; font-weight: 700; margin-bottom: 3px; }
.hrzone-chip .hz-dot { width: 9px; height: 9px; border-radius: 50%; flex: 0 0 auto; }
.hrzone-chip .hz-range { color: var(--text-secondary); font-variant-numeric: tabular-nums; }
.hrzone-chip .hz-purpose { color: var(--text-muted); margin-top: 3px; }
.chart-box.tiny { height: 56px; }
.chart-box.runs-hz { height: 280px; }
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
    <div class="card">
      <div class="card-head">
        <div>
          <h3>Heart rate zone distribution</h3>
          <div class="card-note">Last <span id="hrzone-days-n"></span> days, from Garmin's own per-run zone data (<span id="hrzone-source-note"></span>).</div>
        </div>
      </div>
      <div class="hrzone-defs" id="hrzone-defs"></div>
      <div class="note-banner small" id="hrzone-empty-note" style="display:none;"></div>
      <div id="hrzone-agg-wrap">
        <div class="chart-box tiny"><canvas id="chart-hrzone-agg"></canvas></div>
      </div>
    </div>
    <div class="card" id="hrzone-runs-wrap">
      <div class="card-head">
        <div><h3>Zone breakdown per run</h3><div class="card-note">Each bar is one run, stacked to 100%.</div></div>
        <button class="table-btn" data-toggle="table-hrzone-runs">Table</button>
      </div>
      <div class="chart-box runs-hz"><canvas id="chart-hrzone-runs"></canvas></div>
      <div class="table-wrap"><table class="data-table" id="table-hrzone-runs"></table></div>
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

<div class="modal-overlay" id="metric-modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <div class="modal">
    <div class="modal-head">
      <div>
        <h2 id="modal-title"></h2>
        <div class="modal-subtitle" id="modal-subtitle"></div>
      </div>
      <button class="modal-close" id="modal-close" aria-label="Close">&times;</button>
    </div>
    <div class="modal-chart" id="modal-chart-wrap"><canvas id="modal-chart-canvas"></canvas></div>
    <div id="modal-body"></div>
  </div>
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
    ["5K", cur && cur["5k_s"], "5K", "pred-5k"],
    ["10K", cur && cur["10k_s"], "10K", "pred-10k"],
    ["Half Marathon", cur && cur["half_s"], "Half Marathon", "pred-half"],
    ["Marathon", cur && cur["marathon_s"], "Marathon", "pred-marathon"],
  ];
  defs.forEach(([label, secs, pbKey, key]) => {
    const pb = DATA.personal_bests[pbKey];
    const div = document.createElement("div");
    div.className = "pred-tile";
    div.tabIndex = 0;
    div.setAttribute("role", "button");
    div.setAttribute("aria-haspopup", "dialog");
    div.dataset.metric = key;
    div.innerHTML = `<div class="dist">${label} predicted</div>
      <div class="time">${secs ? fmtTimeShort(secs) : "–"}</div>
      <div class="pb">PB: ${pb ? fmtTimeShort(pb) : "no PB yet"}</div>`;
    div.addEventListener("click", () => openModal(key));
    div.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openModal(key); } });
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
    { key: "fitness", label: "Fitness (CTL, est.)", value: t.fitness, unit: "", spark: DATA.training_load.map(p => p.ctl), color: "var(--series-1)", id: "spark-fitness" },
    { key: "fatigue", label: "Fatigue (ATL, est.)", value: t.fatigue, unit: "", spark: DATA.training_load.map(p => p.atl), color: "var(--series-2)", id: "spark-fatigue" },
    { key: "form", label: "Form (TSB, est.)", value: t.form, unit: "", spark: DATA.training_load.map(p => p.tsb), color: "var(--series-7)", id: "spark-form" },
    { key: "volume", label: "7-day volume", value: null, unit: "", spark: DATA.weekly_mileage.map(w => w.km), color: "var(--series-3)", id: "spark-volume", custom: fmtDist(t.week_km) },
    { key: "vo2max", label: "VO₂ max", value: t.vo2max ?? "–", unit: "", spark: DATA.vo2max.trend.map(p => p.value), color: "var(--series-1)", id: "spark-vo2" },
    { key: "rhr", label: "Resting HR", value: t.resting_hr ?? "–", unit: "bpm", spark: DATA.wellness.rhr.map(p => p.value), color: "var(--series-2)", id: "spark-rhr" },
    { key: "stress", label: "Avg stress", value: t.avg_stress ?? "–", unit: "", spark: DATA.wellness.stress.map(p => p.avg), color: "var(--series-8)", id: "spark-stress" },
    { key: "hrzones", label: "HR zone split (easy %)", value: null, unit: "", spark: DATA.hr_zones.runs.slice().reverse().map(r => r.zone_pct[0] + r.zone_pct[1]), color: "var(--good)", id: "spark-hrzones", custom: (DATA.hr_zones.aggregate.easy_pct ?? "–") + "%" },
  ];
  el.innerHTML = "";
  tiles.forEach(tile => {
    const div = document.createElement("div");
    div.className = "tile";
    div.tabIndex = 0;
    div.setAttribute("role", "button");
    div.setAttribute("aria-haspopup", "dialog");
    div.dataset.metric = tile.key;
    div.innerHTML = `<div class="label">${tile.label}</div>
      <div class="value">${tile.custom ?? tile.value}${tile.unit ? `<span class="u">${tile.unit}</span>` : ""}</div>
      <div class="spark-wrap"><canvas id="${tile.id}"></canvas></div>`;
    div.addEventListener("click", () => openModal(tile.key));
    div.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openModal(tile.key); } });
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

function hrZoneColor(i) {
  const stops = [
    `color-mix(in srgb, ${css("--good")} 55%, ${css("--surface-1")})`,
    css("--good"), css("--warning"), css("--series-2"), css("--critical"),
  ];
  return stops[i];
}

function renderHrZoneDefs() {
  document.getElementById("hrzone-days-n").textContent = DATA.recent_runs_days;
  document.getElementById("hrzone-source-note").textContent = DATA.hr_zones.boundary_source || "";
  const el = document.getElementById("hrzone-defs");
  el.innerHTML = "";
  DATA.hr_zones.zone_defs.forEach((z, i) => {
    const range = (z.high !== null && z.high !== undefined) ? `${z.low}–${z.high} bpm` : `${z.low}+ bpm`;
    const div = document.createElement("div");
    div.className = "hrzone-chip";
    div.innerHTML = `<div class="hz-head"><span class="hz-dot" style="background:${hrZoneColor(i)}"></span>${z.label}</div>
      <div class="hz-range">${range}</div>
      <div class="hz-purpose">${z.purpose}</div>`;
    el.appendChild(div);
  });
}

function renderHrZoneEmptyNote() {
  const el = document.getElementById("hrzone-empty-note");
  const hasData = DATA.hr_zones.runs.length > 0;
  el.style.display = hasData ? "none" : "block";
  if (!hasData) el.textContent = `No per-run heart-rate zone data available yet for the last ${DATA.recent_runs_days} days.`;
  document.getElementById("hrzone-agg-wrap").style.display = hasData ? "" : "none";
  document.getElementById("hrzone-runs-wrap").style.display = hasData ? "" : "none";
}

function renderHrZoneAggChart() {
  destroyChart("hrzoneAgg");
  if (!DATA.hr_zones.runs.length) return;
  const agg = DATA.hr_zones.aggregate;
  const defs = DATA.hr_zones.zone_defs;
  const grid = baseGridOptions();
  charts.hrzoneAgg = new Chart(document.getElementById("chart-hrzone-agg"), {
    type: "bar",
    data: { labels: ["All runs"], datasets: defs.map((z, i) => ({ label: z.label, data: [agg.zone_pct[i]], backgroundColor: hrZoneColor(i), borderRadius: 3 })) },
    options: {
      indexAxis: "y", responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom", labels: { color: css("--text-secondary"), boxWidth: 10, font: { size: 10.5 } } },
        tooltip: { callbacks: { label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.x}%` } },
      },
      scales: {
        x: { stacked: true, min: 0, max: 100, ticks: { ...grid.ticks, callback: v => v + "%" }, grid: grid.grid, border: grid.border },
        y: { stacked: true, ticks: { display: false }, grid: { display: false }, border: grid.border },
      },
    },
  });
}

function renderHrZoneRunsChart() {
  destroyChart("hrzoneRuns");
  const runs = DATA.hr_zones.runs;
  const defs = DATA.hr_zones.zone_defs;
  if (!runs.length) return;
  const grid = baseGridOptions();
  charts.hrzoneRuns = new Chart(document.getElementById("chart-hrzone-runs"), {
    type: "bar",
    data: {
      labels: runs.map(r => fmtDate(r.date)),
      datasets: defs.map((z, i) => ({ label: z.label, data: runs.map(r => r.zone_pct[i]), backgroundColor: hrZoneColor(i), borderRadius: 2, maxBarThickness: 20 })),
    },
    options: {
      indexAxis: "y", responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom", labels: { color: css("--text-secondary"), boxWidth: 10, font: { size: 10.5 } } },
        tooltip: { callbacks: { label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.x}%` } },
      },
      scales: {
        x: { stacked: true, min: 0, max: 100, ticks: { ...grid.ticks, callback: v => v + "%" }, grid: grid.grid, border: grid.border },
        y: { stacked: true, ticks: grid.ticks, grid: { display: false }, border: grid.border },
      },
    },
  });
  buildTable(document.getElementById("table-hrzone-runs"),
    [
      { label: "Date", render: r => fmtDate(r.date) },
      { label: "Run", render: r => r.name || "–" },
      { label: "Distance", render: r => fmtDist(r.distance_km) },
      ...defs.map((z, i) => ({ label: "Z" + (i + 1) + " %", render: r => r.zone_pct[i] + "%" })),
    ],
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

/* ---------- metric detail modal ---------- */
function fmtSigned(v, digits) {
  if (v === null || v === undefined || isNaN(v)) return "–";
  digits = digits === undefined ? 1 : digits;
  return (v > 0 ? "+" : "") + v.toFixed(digits);
}
function fmtGap(sec) {
  if (sec === null || sec === undefined) return "–";
  return (sec < 0 ? "-" : "+") + fmtTimeShort(Math.abs(sec));
}
function statusPill(cls, text) { return `<div class="modal-status status-${cls}">${text}</div>`; }

function modalLineOptions(rows, dateAcc) {
  const grid = baseGridOptions();
  return {
    responsive: true, maintainAspectRatio: false, animation: false,
    interaction: { mode: "index", intersect: false },
    plugins: { legend: { labels: { color: css("--text-secondary"), boxWidth: 10, font: { size: 11 } } } },
    scales: {
      x: { ticks: { ...grid.ticks, maxTicksLimit: 8, callback: (v, i) => fmtDate(dateAcc(rows[i])) }, grid: { display: false }, border: grid.border },
      y: { ticks: grid.ticks, grid: grid.grid, border: grid.border },
    },
  };
}

/* VO2max classification: approximate adult norm bands (general population,
   Cooper-Institute-style mL/kg/min charts), by gender + age bracket. */
const VO2_NORMS = {
  FEMALE: [
    { maxAge: 29, bands: [23, 29, 35, 41, 47] },
    { maxAge: 39, bands: [21, 27, 33, 39, 45] },
    { maxAge: 49, bands: [20, 25, 31, 37, 43] },
    { maxAge: 999, bands: [18, 23, 28, 34, 40] },
  ],
  MALE: [
    { maxAge: 29, bands: [30, 38, 44, 51, 56] },
    { maxAge: 39, bands: [28, 34, 41, 47, 53] },
    { maxAge: 49, bands: [25, 31, 38, 44, 50] },
    { maxAge: 999, bands: [21, 26, 32, 39, 45] },
  ],
};
const VO2_LABELS = ["low", "below average", "average", "good", "very good", "excellent"];
function classifyVo2(vo2, age, gender) {
  const table = VO2_NORMS[gender] || VO2_NORMS.FEMALE;
  const group = table.find(g => (age || 32) <= g.maxAge) || table[table.length - 1];
  let idx = group.bands.findIndex(b => vo2 < b);
  if (idx === -1) idx = group.bands.length;
  return VO2_LABELS[idx];
}

function ctlTrend() {
  const rows = DATA.training_load;
  if (rows.length < 8) return null;
  const now = rows[rows.length - 1].ctl;
  const priorIdx = Math.max(0, rows.length - 1 - 28);
  const prior = rows[priorIdx].ctl;
  return { now, prior, delta: now - prior, days: rows.length - 1 - priorIdx };
}
function loadRatio() {
  const rows = DATA.training_load;
  const latest = rows.length ? rows[rows.length - 1] : { ctl: 0, atl: 0 };
  const ratio = latest.ctl > 0.5 ? latest.atl / latest.ctl : null;
  return { ctl: latest.ctl, atl: latest.atl, tsb: latest.ctl - latest.atl, ratio };
}
function typicalMarathonBand(weeksLeft) {
  if (weeksLeft > 16) return { label: "base phase", lo: 20, hi: 40 };
  if (weeksLeft > 8) return { label: "build phase", lo: 40, hi: 65 };
  if (weeksLeft > 3) return { label: "peak phase", lo: 55, hi: 80 };
  return { label: "taper", lo: 20, hi: 45 };
}
function rhrBaselineVsRecent() {
  const rows = DATA.wellness.rhr;
  if (rows.length < 10) return null;
  const recent = rows.slice(-7);
  const rest = rows.slice(0, -7);
  const avg = arr => arr.reduce((a, b) => a + b.value, 0) / arr.length;
  return { recent: avg(recent), baseline: rest.length ? avg(rest) : avg(recent) };
}
function stressRecentVsPrior() {
  const rows = DATA.wellness.stress;
  if (rows.length < 10) return null;
  const recent = rows.slice(-7);
  const rest = rows.slice(0, -7);
  const avg = arr => arr.reduce((a, b) => a + b.avg, 0) / arr.length;
  return { recent: avg(recent), prior: rest.length ? avg(rest) : avg(recent) };
}
function stressBand(v) {
  if (v === null || v === undefined) return { label: "unknown", cls: "neutral" };
  if (v <= 25) return { label: "rest", cls: "good" };
  if (v <= 50) return { label: "low", cls: "good" };
  if (v <= 75) return { label: "medium", cls: "warn" };
  return { label: "high", cls: "bad" };
}

const METRIC_META = {
  fitness: { title: "Fitness (CTL)", subtitle: () => DATA.stat_tiles.fitness + " · estimated 42-day training load" },
  fatigue: { title: "Fatigue (ATL)", subtitle: () => DATA.stat_tiles.fatigue + " · estimated 7-day training load" },
  form: { title: "Form (TSB)", subtitle: () => DATA.stat_tiles.form + " · fitness minus fatigue" },
  volume: { title: "7-Day Volume", subtitle: () => fmtDist(DATA.stat_tiles.week_km) + " this week" },
  vo2max: { title: "VO₂ max", subtitle: () => (DATA.stat_tiles.vo2max ?? "–") + " mL/kg/min" },
  rhr: { title: "Resting Heart Rate", subtitle: () => (DATA.stat_tiles.resting_hr ?? "–") + " bpm" },
  stress: { title: "Avg Stress", subtitle: () => (DATA.stat_tiles.avg_stress ?? "–") + " / 100" },
  hrzones: { title: "Heart Rate Zone Split", subtitle: () => (DATA.hr_zones.aggregate.easy_pct ?? "–") + "% easy (Z1-Z2), last " + DATA.recent_runs_days + " days" },
  "pred-5k": { title: "5K Prediction", subtitle: () => fmtTimeShort(DATA.predictions.current && DATA.predictions.current["5k_s"]) },
  "pred-10k": { title: "10K Prediction", subtitle: () => fmtTimeShort(DATA.predictions.current && DATA.predictions.current["10k_s"]) },
  "pred-half": { title: "Half Marathon Prediction", subtitle: () => fmtTimeShort(DATA.predictions.current && DATA.predictions.current["half_s"]) },
  "pred-marathon": { title: "Marathon Prediction", subtitle: () => fmtTimeShort(DATA.predictions.current && DATA.predictions.current["marathon_s"]) },
};

function renderModalChart(key) {
  destroyChart("modal");
  const wrap = document.getElementById("modal-chart-wrap");
  const ctx = document.getElementById("modal-chart-canvas");
  let cfg = null;

  if (key === "fitness" || key === "fatigue" || key === "form") {
    const rows = DATA.training_load;
    cfg = {
      type: "line",
      data: {
        labels: rows.map(r => r.date),
        datasets: [
          { label: "Fitness (CTL)", data: rows.map(r => r.ctl), borderColor: css("--series-1"), borderWidth: key === "fitness" ? 2.5 : 1.3, pointRadius: 0, tension: 0.25 },
          { label: "Fatigue (ATL)", data: rows.map(r => r.atl), borderColor: css("--series-2"), borderWidth: key === "fatigue" ? 2.5 : 1.3, pointRadius: 0, tension: 0.25 },
          { label: "Form (TSB)", data: rows.map(r => r.tsb), borderColor: css("--series-7"), borderWidth: key === "form" ? 2.5 : 1.3, pointRadius: 0, tension: 0.25, borderDash: [4, 3] },
        ],
      },
      options: modalLineOptions(rows, r => r.date),
    };
  } else if (key === "volume") {
    const rows = DATA.weekly_mileage;
    const dist = rows.map(r => UNIT === "km" ? r.km : r.km * 0.621371);
    const trend = rows.map(r => UNIT === "km" ? r.trend_km : r.trend_km * 0.621371);
    cfg = {
      data: {
        labels: rows.map(r => r.week_start),
        datasets: [
          { type: "bar", label: "Weekly " + UNIT, data: dist, backgroundColor: css("--series-3"), borderRadius: 4, maxBarThickness: 24 },
          { type: "line", label: "Trend", data: trend, borderColor: css("--series-2"), borderWidth: 2, pointRadius: 0, tension: 0.15 },
        ],
      },
      options: modalLineOptions(rows, r => r.week_start),
    };
  } else if (key === "vo2max") {
    const rows = DATA.vo2max.trend;
    if (rows.length) {
      cfg = {
        type: "line",
        data: { labels: rows.map(r => r.date), datasets: [{ label: "VO₂ max", data: rows.map(r => r.value), borderColor: css("--series-1"), backgroundColor: css("--series-1"), stepped: true, pointRadius: 3, borderWidth: 2 }] },
        options: { ...modalLineOptions(rows, r => r.date), plugins: { legend: { display: false } } },
      };
    }
  } else if (key === "rhr") {
    const rows = DATA.wellness.rhr;
    if (rows.length) {
      cfg = {
        type: "line",
        data: {
          labels: rows.map(r => r.date),
          datasets: [
            { label: "Daily", data: rows.map(r => r.value), borderColor: css("--series-1"), pointRadius: 2, borderWidth: 1.5, tension: 0.2 },
            { label: "7-day avg", data: rows.map(r => r.rolling7), borderColor: css("--series-2"), pointRadius: 0, borderWidth: 2, tension: 0.25 },
          ],
        },
        options: modalLineOptions(rows, r => r.date),
      };
    }
  } else if (key === "stress") {
    const rows = DATA.wellness.stress;
    if (rows.length) {
      cfg = {
        type: "line",
        data: {
          labels: rows.map(r => r.date),
          datasets: [
            { label: "Avg", data: rows.map(r => r.avg), borderColor: css("--series-1"), pointRadius: 0, borderWidth: 2, tension: 0.25 },
            { label: "Max", data: rows.map(r => r.max), borderColor: css("--series-8"), pointRadius: 0, borderWidth: 1.5, borderDash: [3, 3], tension: 0.25 },
          ],
        },
        options: modalLineOptions(rows, r => r.date),
      };
    }
  } else if (key === "hrzones") {
    const runs = DATA.hr_zones.runs;
    const defs = DATA.hr_zones.zone_defs;
    if (runs.length) {
      const grid = baseGridOptions();
      cfg = {
        type: "bar",
        data: {
          labels: runs.map(r => fmtDate(r.date)),
          datasets: defs.map((z, i) => ({ label: z.label, data: runs.map(r => r.zone_pct[i]), backgroundColor: hrZoneColor(i), borderRadius: 2 })),
        },
        options: {
          indexAxis: "y", responsive: true, maintainAspectRatio: false, animation: false,
          plugins: { legend: { position: "bottom", labels: { color: css("--text-secondary"), boxWidth: 10, font: { size: 10.5 } } } },
          scales: {
            x: { stacked: true, min: 0, max: 100, ticks: { ...grid.ticks, callback: v => v + "%" }, grid: grid.grid, border: grid.border },
            y: { stacked: true, ticks: grid.ticks, grid: { display: false }, border: grid.border },
          },
        },
      };
    }
  } else if (key.startsWith("pred-")) {
    const field = { "pred-5k": "5k_s", "pred-10k": "10k_s", "pred-half": "half_s", "pred-marathon": "marathon_s" }[key];
    const hist = (DATA.predictions.history || []).filter(h => h[field]);
    if (hist.length >= 2) {
      cfg = {
        type: "line",
        data: { labels: hist.map(h => h.date), datasets: [{ label: "Predicted (min)", data: hist.map(h => h[field] / 60), borderColor: css("--series-1"), backgroundColor: css("--series-1"), pointRadius: 3, borderWidth: 2, tension: 0.2 }] },
        options: { ...modalLineOptions(hist, r => r.date), plugins: { legend: { display: false } } },
      };
    }
  }

  if (!cfg) {
    wrap.style.display = "none";
    return;
  }
  wrap.style.display = "";
  charts.modal = new Chart(ctx, cfg);
}

function metricContent(key) {
  const t = DATA.stat_tiles;
  const p = DATA.profile;

  if (key === "vo2max") {
    const vo2 = t.vo2max;
    if (vo2 === null || vo2 === undefined) {
      return `<div class="modal-section"><p>No VO₂max reading available yet.</p></div>`;
    }
    const gender = p.gender === "FEMALE" ? "FEMALE" : "MALE";
    const cls = classifyVo2(vo2, p.age, gender);
    const clsPill = { low: "bad", "below average": "warn", average: "warn", good: "good", "very good": "good", excellent: "good" }[cls] || "neutral";
    const ageNote = p.age ? `for a ${p.age}-year-old ${gender === "FEMALE" ? "woman" : "man"}` : "for an adult (age not available from your Garmin profile)";
    return `
      <div class="modal-section">
        <h4>What it measures</h4>
        <p>VO₂max is the maximum rate your body can consume oxygen during exercise (mL of O₂ per kg of body weight per minute). It's a hard ceiling on aerobic capacity &mdash; a higher number means more fuel available for aerobic running effort, which generally correlates with faster sustainable race paces.</p>
      </div>
      <div class="modal-section">
        <h4>Where you stand</h4>
        ${statusPill(clsPill, cls)}
        <p>${vo2} mL/kg/min falls in the <b>${cls}</b> band on general-population adult norm charts ${ageNote}. Note these general-population bands undersell trained runners: among competitive ${gender === "FEMALE" ? "female" : "male"} distance runners, ${gender === "FEMALE" ? "45-55 is a strong sub-elite range and 55-70+ is elite" : "50-60 is strong sub-elite and 60-75+ is elite"} &mdash; so ${vo2} is a genuinely strong aerobic engine, with room to keep climbing through targeted training.</p>
      </div>
      <div class="modal-section">
        <h4>How to raise it</h4>
        <ul>
          <li><b>VO₂max intervals</b> at ~3K&ndash;5K effort: e.g. 5&ndash;6 &times; 3min hard (roughly current 5K pace) with 2&ndash;3min easy jog recovery. This is the most direct stimulus for raising the ceiling itself.</li>
          <li><b>Tempo/threshold runs</b> at ${p.threshold_hr ? p.threshold_hr + " bpm" : "your threshold HR"}, 20&ndash;30min continuous: raises how much of that ceiling you can sustain, which is what actually shows up in race times.</li>
          <li><b>Aerobic volume</b>: easy mileage doesn't move VO₂max much directly but supports recovery between hard sessions, letting you hit them at full quality.</li>
        </ul>
      </div>
      <div class="modal-section">
        <h4>Realistic timeline</h4>
        <p>For someone already in the good-to-excellent range, a focused 8&ndash;12 week block with 1&ndash;2 quality sessions/week typically yields ~1&ndash;3 mL/kg/min (roughly 2&ndash;6% relative). Gains get harder as you approach your genetic ceiling &mdash; consistency over months matters more than any single workout.</p>
        <h4>This week</h4>
        <ul>
          <li>1 VO₂max session: 5 &times; 3min @ 5K effort / 2min jog recovery.</li>
          <li>1 tempo run: 20&ndash;25min continuous at threshold effort.</li>
          <li>Keep 2&ndash;3 easy aerobic days around them &mdash; don't stack hard days back-to-back.</li>
        </ul>
      </div>`;
  }

  if (key === "fitness") {
    const trend = ctlTrend();
    const rows = DATA.plan.weeks || [];
    const peak = rows.length ? rows.reduce((a, b) => (b.target_km > a.target_km ? b : a)) : null;
    let trendText = "Not enough training history yet to establish a trend.";
    let pill = statusPill("neutral", "insufficient data");
    if (trend) {
      const dir = trend.delta > 0.5 ? "risen" : trend.delta < -0.5 ? "fallen" : "held roughly steady";
      const pillCls = trend.delta > 0.5 ? "good" : trend.delta < -0.5 ? "bad" : "neutral";
      pill = statusPill(pillCls, dir === "held roughly steady" ? "stagnant" : dir);
      trendText = `Over the last ${trend.days} days your estimated Fitness has ${dir}, from ${trend.prior.toFixed(1)} to ${trend.now.toFixed(1)} (${fmtSigned(trend.delta)}).`;
    }
    return `
      <div class="modal-section">
        <h4>What it measures</h4>
        <p>Fitness (CTL) is your accumulated training load, averaged with a slow 42-day time constant &mdash; it reflects the aerobic base you've built over the last month and a half, not any single run. It rises slowly and falls slowly, by design.</p>
      </div>
      <div class="modal-section">
        <h4>Your trend</h4>
        ${pill}
        <p>${trendText}</p>
      </div>
      <div class="modal-section">
        <h4>Building toward race day</h4>
        <p>Your generated Plan targets a peak week of ${peak ? fmtDist(peak.target_km) : "–"}${peak ? " around week " + peak.week_num : ""}. Fitness only rises if training load keeps climbing week over week &mdash; the standard safe progression is <b>no more than ~10% weekly volume increase</b>, with a lighter down-week roughly every 3&ndash;4 weeks to let CTL consolidate instead of just chasing ATL spikes. If Fitness looks flat, the usual cause is a mileage plateau, not a training-response problem &mdash; check the Plan section for whether you're actually hitting target volumes.</p>
      </div>`;
  }

  if (key === "fatigue") {
    const lr = loadRatio();
    let pill, advice;
    if (lr.ratio === null) {
      pill = statusPill("neutral", "insufficient data");
      advice = "Not enough training history yet to compute a reliable Fatigue-to-Fitness ratio.";
    } else if (lr.ratio > 1.5) {
      pill = statusPill("bad", "high &mdash; overreaching risk");
      advice = "Fatigue is climbing meaningfully faster than Fitness &mdash; classic overreaching territory. Add an extra easy or full rest day this week, and downgrade your next scheduled hard session to an easy aerobic run until Form (TSB) recovers back toward zero.";
    } else if (lr.ratio > 1.3) {
      pill = statusPill("warn", "elevated");
      advice = "Fatigue is running a bit ahead of Fitness. Not an emergency, but worth watching &mdash; keep an eye on sleep, easy-run heart rate drift, and how the next hard session feels before adding more load.";
    } else if (lr.ratio >= 0.8) {
      pill = statusPill("good", "productive zone");
      advice = "This is a normal, productive training relationship between short-term and long-term load &mdash; fatigue rising a bit while fitness catches up is exactly what a training block should look like.";
    } else {
      pill = statusPill("neutral", "low load");
      advice = "Fatigue is well below Fitness right now, meaning recent training load has been light relative to your base &mdash; fine during a taper or recovery week, but a signal to add volume if you're mid-build.";
    }
    return `
      <div class="modal-section">
        <h4>What it measures</h4>
        <p>Fatigue (ATL) is short-term training load, averaged with a fast 7-day time constant. It reacts quickly to what you did this week, unlike the slow-moving Fitness number.</p>
      </div>
      <div class="modal-section">
        <h4>Overtraining check</h4>
        ${pill}
        <p>Fatigue/Fitness ratio: ${lr.ratio !== null ? lr.ratio.toFixed(2) : "–"} (ATL ${lr.atl.toFixed(1)} vs CTL ${lr.ctl.toFixed(1)}). As a rough guide: 0.8&ndash;1.3 is a healthy training zone, 1.3&ndash;1.5 is elevated, and above 1.5 tracks with classic overreaching/injury-risk ranges (the same logic behind acute:chronic workload ratio guidance used in sports science).</p>
        <p>${advice}</p>
      </div>`;
  }

  if (key === "form") {
    const lr = loadRatio();
    const tsb = lr.tsb;
    let pill, band;
    if (tsb < -30) { pill = statusPill("bad", "very fatigued"); band = "Below -30 usually means you're carrying heavy accumulated fatigue &mdash; fine briefly at peak training load, risky to sit in for long."; }
    else if (tsb < -10) { pill = statusPill("warn", "in training"); band = "-10 to -30 is typical of solid build/peak training blocks &mdash; you're absorbing real load, which is the point, but it's not a day to expect a fast time trial."; }
    else if (tsb <= 5) { pill = statusPill("neutral", "grey zone"); band = "-10 to +5 is a neutral zone &mdash; neither notably fatigued nor fresh."; }
    else if (tsb <= 25) { pill = statusPill("good", "fresh"); band = "+5 to +25 is a fresh, race-ready zone &mdash; this is roughly where you want to be on race morning."; }
    else { pill = statusPill("neutral", "very fresh"); band = "Above +25 usually means you've backed off more than needed &mdash; fine right before a race, a detraining risk if it persists for weeks."; }

    const raceDate = new Date(DATA.race.date + "T00:00:00");
    const taperStart = new Date(raceDate);
    taperStart.setDate(taperStart.getDate() - 18);
    const taperStr = taperStart.toISOString().slice(0, 10);
    const weeksLeft = DATA.race.weeks_left;

    return `
      <div class="modal-section">
        <h4>What it measures</h4>
        <p>Form (TSB) is Fitness minus Fatigue &mdash; a "freshness" score. Negative means you're carrying more short-term fatigue than your base can currently absorb (typical while training hard); positive means you've shed fatigue faster than fitness, i.e. you're fresh.</p>
      </div>
      <div class="modal-section">
        <h4>Reading your number</h4>
        ${pill}
        <p>Current TSB: ${tsb.toFixed(1)}. ${band}</p>
      </div>
      <div class="modal-section">
        <h4>Planning your taper</h4>
        <p>You're about ${weeksLeft} weeks from ${DATA.race.name}. A typical marathon taper starts 2&ndash;3 weeks out (around <b>${fmtDate(taperStr)}</b> for your race date), cutting weekly volume by roughly 20&ndash;40% while keeping some race-pace touches, with the goal of arriving at the start line with TSB back in the fresh +5 to +15 range rather than deep in the negatives.</p>
      </div>`;
  }

  if (key === "volume") {
    const weeksLeft = DATA.race.weeks_left;
    const band = typicalMarathonBand(weeksLeft);
    const weekKm = t.week_km;
    const status = weekKm < band.lo ? "under" : weekKm > band.hi ? "over" : "within";
    const pill = status === "under" ? statusPill("warn", "below typical range") : status === "over" ? statusPill("good", "above typical range") : statusPill("good", "within typical range");
    const next1 = Math.round(weekKm * 1.1 * 10) / 10;
    const next2 = Math.round(next1 * 1.1 * 10) / 10;
    return `
      <div class="modal-section">
        <h4>Where this fits your marathon block</h4>
        ${pill}
        <p>At ${weeksLeft} weeks out, a typical recreational marathon block is in its <b>${band.label}</b>, commonly running <b>${band.lo}&ndash;${band.hi} km/week</b>. Your current week is <b>${fmtDist(weekKm)}</b> &mdash; ${status === "under" ? "meaningfully below that range, which is the main thing worth addressing before anything else in this plan" : status === "over" ? "above the typical range, which is fine if it's been progressive and recovery is keeping up" : "within the typical range for this stage"}.</p>
      </div>
      <div class="modal-section">
        <h4>Next 2 weeks</h4>
        <p>Using a conservative ~10%/week ramp from your current volume: <b>${fmtDist(next1)}</b> next week, then <b>${fmtDist(next2)}</b> the week after, with easy pace on the added distance. If that still leaves you short of the block's typical range with limited weeks left, prioritize consistency (running more often, even short) over any single long run.</p>
      </div>`;
  }

  if (key === "rhr") {
    const cmp = rhrBaselineVsRecent();
    let pill, text;
    if (!cmp) {
      pill = statusPill("neutral", "insufficient data");
      text = "Not enough resting-HR history yet to compare recent readings against a baseline.";
    } else {
      const delta = cmp.recent - cmp.baseline;
      if (delta >= 7) { pill = statusPill("bad", "notably elevated"); text = `Your last 7 days average ${cmp.recent.toFixed(1)} bpm vs a ${cmp.baseline.toFixed(1)} bpm baseline &mdash; a jump of ${fmtSigned(delta)} bpm is a meaningful signal (illness, poor sleep, or under-recovery are common causes). Worth an easier few days.`; }
      else if (delta >= 4) { pill = statusPill("warn", "slightly elevated"); text = `Last 7 days average ${cmp.recent.toFixed(1)} bpm vs baseline ${cmp.baseline.toFixed(1)} bpm (${fmtSigned(delta)} bpm). Not alarming on its own, but worth watching alongside how easy runs are feeling.`; }
      else if (delta <= -3) { pill = statusPill("good", "trending down"); text = `Last 7 days average ${cmp.recent.toFixed(1)} bpm vs baseline ${cmp.baseline.toFixed(1)} bpm (${fmtSigned(delta)} bpm) &mdash; a falling RHR is generally a good sign of improving aerobic fitness and recovery.`; }
      else { pill = statusPill("good", "stable"); text = `Last 7 days average ${cmp.recent.toFixed(1)} bpm vs baseline ${cmp.baseline.toFixed(1)} bpm &mdash; essentially stable, no recovery flag.`; }
    }
    return `
      <div class="modal-section">
        <h4>What it indicates</h4>
        <p>Resting heart rate reflects how hard your heart works at rest, mainly driven by cardiovascular fitness and recovery state. A gradually falling RHR over weeks/months usually tracks improving aerobic fitness; a sudden rise of several bpm above your personal baseline for multiple consecutive days is a common early flag for under-recovery, incoming illness, or accumulated fatigue &mdash; more useful as a trend than any single day's reading.</p>
      </div>
      <div class="modal-section">
        <h4>Your recent trend</h4>
        ${pill}
        <p>${text}</p>
      </div>`;
  }

  if (key === "stress") {
    const cmp = stressRecentVsPrior();
    const band = stressBand(t.avg_stress);
    let trendText = "Not enough stress history yet to compare recent days against prior weeks.";
    if (cmp) {
      const delta = cmp.recent - cmp.prior;
      trendText = `Last 7 days average ${cmp.recent.toFixed(0)} vs ${cmp.prior.toFixed(0)} in the prior period (${fmtSigned(delta, 0)}).`;
    }
    return `
      <div class="modal-section">
        <h4>What it measures</h4>
        <p>Garmin's stress score (0&ndash;100) is derived from heart-rate-variability patterns through the day. Garmin's own bands: 0&ndash;25 <i>resting</i>, 26&ndash;50 <i>low</i>, 51&ndash;75 <i>medium</i>, 76&ndash;100 <i>high</i>. It reflects overall physiological stress, not just training &mdash; sleep, illness and life stress all feed into it.</p>
      </div>
      <div class="modal-section">
        <h4>Where you are</h4>
        ${statusPill(band.cls, band.label + " band")}
        <p>Current average: ${t.avg_stress ?? "–"}/100. ${trendText} ${band.cls === "warn" || band.cls === "bad" ? "A sustained average in the medium-to-high band alongside hard training weeks is a reasonable cue to prioritize sleep and add easy/recovery days before adding more training stress." : "This is a comfortable range &mdash; no particular recovery flag from stress alone right now."}</p>
      </div>`;
  }

  if (key === "hrzones") {
    const agg = DATA.hr_zones.aggregate;
    if (agg.easy_pct === null || agg.easy_pct === undefined) {
      return `<div class="modal-section"><p>Not enough per-run heart-rate zone data yet for the last ${DATA.recent_runs_days} days.</p></div>`;
    }
    const easy = agg.easy_pct, tempo = agg.tempo_pct, hard = agg.hard_pct;
    let pill, verdict;
    if (easy >= 78) {
      pill = statusPill("good", "on target");
      verdict = `Your easy/hard split (${easy}% easy) is right around the 80/20 guideline &mdash; keep doing what you're doing.`;
    } else if (easy >= 65) {
      pill = statusPill("warn", "slightly off");
      verdict = `At ${easy}% easy, you're a bit below the 80/20 target. The most common cause is "easy" runs drifting into Z3 &mdash; ${tempo}% of your time is in Z3 (Tempo) right now, which is high if most of those runs were meant to be easy.`;
    } else {
      pill = statusPill("bad", "too much hard running");
      verdict = `At only ${easy}% easy, you're well below the 80/20 target, with ${hard}% of your time in Z4-Z5. That much hard-running load without a large easy base raises injury and burnout risk, especially heading into a marathon build.`;
    }
    return `
      <div class="modal-section">
        <h4>The 80/20 rule</h4>
        <p>Polarized-training research (Seiler et al.) consistently finds that runners who spend roughly <b>80% of training time easy</b> (Z1&ndash;Z2, conversational effort) and <b>~20% hard</b> (Z3&ndash;Z5, ideally concentrated at Z4&ndash;Z5 rather than a moderate Z3 grey zone) improve faster and get injured less than those parked at a comfortably-hard middle intensity most days. Z3 is the zone runners drift into by accident &mdash; it feels productive but is often too hard to recover from and too easy to build real fitness.</p>
      </div>
      <div class="modal-section">
        <h4>Your current split</h4>
        ${pill}
        <p>Last ${DATA.recent_runs_days} days: <b>${easy}%</b> easy (Z1&ndash;Z2), <b>${tempo}%</b> tempo (Z3), <b>${hard}%</b> hard (Z4&ndash;Z5).</p>
        <p>${verdict}</p>
      </div>
      <div class="modal-section">
        <h4>What to adjust</h4>
        <ul>
          <li>If Z3 is high: deliberately slow down easy runs &mdash; if you can't hold a conversation, you're not in Z2. It should feel almost too easy.</li>
          <li>If Z4&ndash;Z5 is high without dedicated interval sessions: check whether "easy" days are creeping into threshold effort, or whether recovery runs are being pushed too hard.</li>
          <li>Keep 1&ndash;2 sessions a week genuinely hard (intervals/tempo) and let everything else be genuinely easy &mdash; avoid the moderate middle ground on non-workout days.</li>
        </ul>
      </div>`;
  }

  if (key.startsWith("pred-")) {
    const meta = { "pred-5k": ["5k_s", "5K", "5K"], "pred-10k": ["10k_s", "10K", "10K"], "pred-half": ["half_s", "Half Marathon", "half marathon"], "pred-marathon": ["marathon_s", "Marathon", "marathon"] }[key];
    const [field, pbKey, label] = meta;
    const predicted = DATA.predictions.current && DATA.predictions.current[field];
    const pb = DATA.personal_bests[pbKey];
    const gap = (predicted && pb) ? predicted - pb : null;
    const focus = {
      "5K": "Short, fast VO₂max-pace repeats (400&ndash;800m at or slightly faster than current 5K pace, full recovery) plus general speed/running-economy work close the 5K gap fastest &mdash; this distance is the most sensitive to raw VO₂max and neuromuscular speed.",
      "10K": "A blend of VO₂max intervals and lactate-threshold/tempo work. 10K sits between pure aerobic-power and sustained-threshold demands, so alternating interval weeks with tempo weeks tends to move it fastest.",
      "half marathon": "Threshold/tempo work is the priority here &mdash; sustained efforts at or near half-marathon pace (20&ndash;40min continuous or in long intervals), plus long runs with race-pace segments woven in.",
      "marathon": "Aerobic volume and long runs dominate marathon-specific improvement, with marathon-pace segments inside long runs and fueling/pacing practice. Threshold work still matters, but raw endurance and fat-utilization economy move this number more than short intervals do.",
    }[label];
    let gapText;
    if (predicted && pb) {
      gapText = gap < 0
        ? `Your current fitness predicts a time <b>${fmtTimeShort(Math.abs(gap))} faster</b> than your PB &mdash; you may be in shape for a new PR attempt on this distance right now.`
        : `Predicted time is <b>${fmtTimeShort(gap)} slower</b> than your PB. That's normal &mdash; predictions track current fitness, and a strong PB can reflect a peak-fitness/perfect-conditions day that current training hasn't caught back up to yet.`;
    } else if (predicted) {
      gapText = "You don't have a recorded PB for this distance yet &mdash; this predicted time is your current fitness ceiling estimate for it.";
    } else {
      gapText = "No prediction available for this distance yet.";
    }
    return `
      <div class="modal-section">
        <h4>How this is calculated</h4>
        <p>Garmin derives race predictions primarily from your current VO₂max estimate combined with recent training history, using a VDOT/Daniels-Gilbert-style formula &mdash; not from a single time trial. That means the number moves as your VO₂max and training load change, and can lag behind (or run ahead of) a single standout or off race performance.</p>
      </div>
      <div class="modal-section">
        <h4>Gap to your PB</h4>
        <p>${gapText}</p>
      </div>
      <div class="modal-section">
        <h4>What closes this gap fastest</h4>
        <p>${focus}</p>
      </div>`;
  }

  return `<div class="modal-section"><p>No detail available.</p></div>`;
}

let lastModalTrigger = null;
function openModal(key) {
  lastModalTrigger = document.activeElement;
  const meta = METRIC_META[key];
  if (!meta) return;
  document.getElementById("modal-title").textContent = meta.title;
  document.getElementById("modal-subtitle").textContent = meta.subtitle();
  document.getElementById("modal-body").innerHTML = metricContent(key);
  renderModalChart(key);
  const overlay = document.getElementById("metric-modal");
  overlay.classList.add("open");
  document.body.style.overflow = "hidden";
  document.getElementById("modal-close").focus();
}
function closeModal() {
  const overlay = document.getElementById("metric-modal");
  if (!overlay.classList.contains("open")) return;
  overlay.classList.remove("open");
  document.body.style.overflow = "";
  destroyChart("modal");
  if (lastModalTrigger && typeof lastModalTrigger.focus === "function") lastModalTrigger.focus();
}
document.getElementById("modal-close").addEventListener("click", closeModal);
document.getElementById("metric-modal").addEventListener("click", (e) => {
  if (e.target.id === "metric-modal") closeModal();
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeModal();
});

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
  renderHrZoneDefs();
  renderHrZoneEmptyNote();
  renderHrZoneAggChart();
  renderHrZoneRunsChart();
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
