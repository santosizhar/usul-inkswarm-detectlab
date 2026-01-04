from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List
from datetime import datetime, timezone

from ..config import AppConfig
from ..io.paths import run_dir as run_dir_for
from .summarize import write_ui_summary, build_ui_summary


def _now_utc_short() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def export_ui_bundle(
    cfg: AppConfig,
    *,
    run_ids: list[str],
    out_dir: Path,
    force: bool = False,
) -> Path:
    """Export a self-contained static HTML bundle for up to 5 run_ids.

    Design goals:
    - Shareable: open index.html directly (no server, no CORS fetch).
    - Stakeholder-friendly: headline tables, low jargon.
    """
    run_ids = [r.strip() for r in run_ids if r.strip()]
    if not run_ids:
        raise ValueError("No run_ids provided.")
    if len(run_ids) > 5:
        raise ValueError("UI v1 supports at most 5 run_ids (nmax=5).")

    out_dir.mkdir(parents=True, exist_ok=True)
    index_path = out_dir / "index.html"
    app_path = out_dir / "app.js"
    css_path = out_dir / "style.css"

    # Build summaries (write into runs/<run_id>/ui first, then embed)
    summaries: list[dict[str, Any]] = []
    for rid in run_ids:
        write_ui_summary(cfg, run_id=rid, force=force)
        summaries.append(build_ui_summary(cfg, run_id=rid))

    # Static assets (minimal)
    index_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Inkswarm DetectLab — MVP Results Viewer</title>
  <link rel="stylesheet" href="style.css"/>
</head>
<body>
  <header class="top">
    <div class="wrap">
      <div class="title">Inkswarm DetectLab — MVP Results Viewer</div>
      <div class="subtitle">Stakeholder-friendly comparison of up to 5 runs — <b>user_holdout</b> = generalization to new users (primary), <b>time_eval</b> = time drift check (secondary).</div>
      <div class="meta">Generated: {_now_utc_short()}</div>
    </div>
  </header>

  <main class="wrap">
    <section class="controls">
      <div class="control">
        <label for="metric">View focus</label>
        <select id="metric">
          <option value="user_holdout" selected>User Holdout (primary)</option>
          <option value="time_eval">Time Eval (drift check)</option>
        </select>
      </div>
      <div class="control">
        <label for="detail">Detail level</label>
        <select id="detail">
          <option value="summary">Summary</option>
          <option value="detailed">Detailed</option>
        </select>
      </div>
<div class="control">
  <label for="goto">Go to run</label>
  <select id="goto">
    <option value="" selected>Select a run…</option>
  </select>
</div>
      <div class="hint">
        Tip: Share this folder as-is. Open <code>index.html</code> in any modern browser.
      </div>
</section>

<section class="banner" id="overview">
  <span class="badge">Truth split</span>
  <div><b>User Holdout</b> is the primary evaluation (generalization). <b>Time Eval</b> is the drift check.</div>
</section>

<div id="content"></div>

    <section class="foot">
      <h2>How to interpret</h2>
      <ul>
        <li><b>PR-AUC</b> (higher is better) is a good headline metric for rare positives.</li>
        <li><b>Recall @ 1% FPR</b> shows how many true positives you catch while keeping false alarms low.</li>
        <li><b>Time Eval</b> tests stability over time; <b>User Holdout</b> tests generalization to new users.</li>
        <li><b>Run signature</b> shows config hash and (if available) code hash for traceability.</li>
      </ul>
    </section>
  </main>

  <script src="app.js"></script>
</body>
</html>
"""
    css = """
:root { --bg:#0b0e14; --panel:#121827; --text:#e7eaf0; --muted:#9aa4b2; --line:#243047; --accent:#7aa2ff; --good:#6ee7b7; --bad:#fb7185; }
*{box-sizing:border-box}
body{margin:0;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial; background:var(--bg); color:var(--text)}
.wrap{max-width:1100px;margin:0 auto;padding:20px}
.top{border-bottom:1px solid var(--line); background:linear-gradient(180deg,#121827, #0b0e14)}
.title{font-size:22px;font-weight:700}
.subtitle{color:var(--muted); margin-top:4px}
.meta{color:var(--muted); margin-top:8px; font-size:12px}
.controls{display:flex; gap:16px; align-items:flex-end; flex-wrap:wrap; margin:14px 0 18px}
.control{display:flex; flex-direction:column; gap:6px; min-width:220px}
label{color:var(--muted); font-size:12px}
select{background:var(--panel); border:1px solid var(--line); color:var(--text); padding:10px; border-radius:10px}
.hint{color:var(--muted); font-size:12px; padding:10px 12px; border:1px dashed var(--line); border-radius:10px; flex: 1}
.banner{display:flex; gap:12px; align-items:center; padding:12px 14px; border:1px solid var(--line); border-radius:12px; background:rgba(122,162,255,0.08); margin:0 0 12px}
.badge{display:inline-block; padding:3px 10px; border-radius:999px; border:1px solid var(--line); background:rgba(255,255,255,0.02); color:var(--muted); font-size:12px}
.kv .pill.missing{opacity:0.85}
.card{background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:16px; margin-bottom:14px}
.card h2{margin:0 0 8px; font-size:16px}
.small{color:var(--muted); font-size:12px}
table{width:100%; border-collapse:collapse; margin-top:10px}
th,td{border-bottom:1px solid var(--line); padding:10px; text-align:left; vertical-align:top}
th{color:var(--muted); font-weight:600; font-size:12px}
.badge{display:inline-block; padding:2px 8px; border-radius:999px; border:1px solid var(--line); color:var(--muted); font-size:12px}
.kv{display:flex; gap:10px; flex-wrap:wrap; margin-top:8px}
.kv .pill{border:1px solid var(--line); border-radius:999px; padding:6px 10px; color:var(--muted); font-size:12px}
.ok{color:var(--good)}
.fail{color:var(--bad)}
code{background:#0f1626; border:1px solid var(--line); padding:2px 6px; border-radius:6px}
.foot{margin-top:18px; color:var(--muted)}
.foot h2{color:var(--text); font-size:14px}

.panel{margin-top:12px;padding:12px;border:1px solid var(--line);border-radius:12px;background:rgba(255,255,255,0.02)}
.mini{width:100%;border-collapse:collapse;margin-top:8px}
.mini th,.mini td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;font-size:12px}
.warn{color:#fbbf24;font-weight:600}
""".strip() + "\n"

    # app.js embeds all data to avoid fetch/CORS issues on file://
    data = {"schema_version": 1, "generated_at_utc": _now_utc_short(), "runs": summaries}
    app_js = f"""/* Inkswarm DetectLab — MVP Results Viewer (static) */
window.__RUN_DATA__ = {json.dumps(data, indent=2)};
(function() {{
  const $ = (id) => document.getElementById(id);
  const content = $("content");
  const metricSel = $("metric");
  const detailSel = $("detail");
  const gotoSel = $("goto");

  function fmt(x) {{
    if (x === null || x === undefined) return "—";
    if (typeof x === "number") return x.toFixed(4);
    return String(x);
  }}

  function pickCell(entry, metricKey, detail) {{
    if (!entry || entry.status !== "ok") {{
      const err = entry && entry.error ? entry.error : "missing";
      return `<span class="fail">failed</span><div class="small">${{err}}</div>`;
    }}
    const split = entry[metricKey] || {{}};
    if (detail === "summary") {{
      return `
        <div><span class="badge">PR-AUC</span> <b>${{fmt(split.pr_auc)}}</b></div>
        <div class="small">Recall @ train thr: <b>${{fmt(split.recall)}}</b> (FPR=${{fmt(split.fpr)}})</div>
      `;
    }}
    return `
      <div><span class="badge">PR-AUC</span> <b>${{fmt(split.pr_auc)}}</b></div>
      <div class="small">Threshold used: <code>${{fmt(split.threshold_used ?? entry.train?.threshold_for_fpr)}}</code></div>
      <div class="small">Recall: <b>${{fmt(split.recall)}}</b> • Precision: <b>${{fmt(split.precision)}}</b> • FPR: <b>${{fmt(split.fpr)}}</b></div>
      <div class="small">ROC-AUC: <b>${{fmt(split.roc_auc)}}</b></div>
    `;
  }}

  function render() {{
    const metricKey = metricSel.value;
    const detail = detailSel.value;
    const runs = (window.__RUN_DATA__ && window.__RUN_DATA__.runs) || [];
if (gotoSel && !gotoSel.dataset.ready) {{
  const esc = (s) => String(s)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  const opts = ['<option value="" selected>Select a run…</option>']
    .concat(runs.map((r) => {{
      const v = r.run_id || "";
      const safe = esc(v);
      return `<option value="${{safe}}">${{safe}}</option>`;
    }}));
  gotoSel.innerHTML = opts.join("");
  gotoSel.addEventListener("change", () => {{
    const v = gotoSel.value;
    if (!v) return;
    const a = encodeURIComponent(v);
    const el = document.getElementById(`run-${{a}}`);
    if (el) el.scrollIntoView({{behavior: "smooth", block: "start"}});
  }});
  gotoSel.dataset.ready = "1";
}}

    content.innerHTML = "";

    runs.forEach((r) => {{
      const base = r.baselines && r.baselines.login_attempt;
      const labels = base && base.labels ? base.labels : {{}};
      const target = base && base.target_fpr;
      const env = base && base.meta && base.meta.env ? base.meta.env : null;
      const sig = r.signature || null;

      const noteBits = [];
      if (target !== null && target !== undefined) noteBits.push(`<span class="pill">Target FPR: <b>${{fmt(target)}}</b></span>`);
      if (env && env.python) noteBits.push(`<span class="pill">Python: <b>${{env.python.split(" ")[0]}}</b></span>`);
      if (env && env.platform) noteBits.push(`<span class="pill">Platform: <b>${{env.platform}}</b></span>`);if (sig && sig.config_hash) {{
  noteBits.push(`<span class="pill" title="${{sig.config_hash}}">Config: <b>${{sig.config_hash.slice(0,8)}}</b></span>`);
}} else {{
  noteBits.push(`<span class="pill missing">Config: <b>—</b></span>`);
}}
if (sig && sig.github_sha) {{
  noteBits.push(`<span class="pill" title="${{sig.github_sha}}">Code: <b>${{sig.github_sha.slice(0,8)}}</b></span>`);
}} else {{
  noteBits.push(`<span class="pill missing">Code: <b>(no git)</b></span>`);
}}

      const card = document.createElement("section");
      card.className = "card";
      card.innerHTML = `
        <h2 id="run-${{encodeURIComponent(r.run_id || '')}}">Run: <code>${{r.run_id}}</code></h2>
        <div class="small">Generated: ${{r.generated_at_utc || "—"}} • Timezone: ${{r.timezone || "—"}}</div>
        <div class="kv">${{noteBits.join("")}}</div>
      `;

      const tbl = document.createElement("table");
      const head = document.createElement("thead");
      head.innerHTML = `<tr><th>Label</th><th>logreg</th><th>rf</th></tr>`;
      tbl.appendChild(head);

      const body = document.createElement("tbody");
      const labelNames = Object.keys(labels).sort();
      if (labelNames.length === 0) {{
        const tr = document.createElement("tr");
        tr.innerHTML = `<td colspan="3"><span class="fail">No baselines found</span><div class="small">Run may be pre-baselines or baselines failed.</div></td>`;
        body.appendChild(tr);
      }} else {{
        labelNames.forEach((lab) => {{
          const byModel = labels[lab] || {{}};
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td><b>${{lab}}</b></td>
            <td>${{pickCell(byModel.logreg, metricKey, detail)}}</td>
            <td>${{pickCell(byModel.rf, metricKey, detail)}}</td>
          `;
          body.appendChild(tr);
        }});
      }}
      tbl.appendChild(body);
      card.appendChild(tbl);


      // Diagnostics (Slices + Stability)
      const ev = r.eval && r.eval.login_attempt ? r.eval.login_attempt : null;
      if (ev) {{
        const diag = document.createElement("div");
        diag.className = "panel";
        let html = `<h3>Diagnostics</h3>`;
        if (ev.stability_summary && ev.stability_summary.rows && ev.stability_summary.rows.length) {{
          const rows = ev.stability_summary.rows.slice(0);
          html += `<div class="small">Primary truth split: <b>${{ev.stability_summary.primary_split || "user_holdout"}}</b></div>`;
          html += `<table class="mini"><thead><tr><th>Label</th><th>Model</th><th>Holdout PR-AUC</th><th>Holdout Recall@thr</th><th>Time Recall@thr</th><th>ΔRecall (Hold-Time)</th></tr></thead><tbody>`;
          rows.forEach((rr) => {{
            html += `<tr><td><code>${{rr.label}}</code></td><td><code>${{rr.model}}</code></td><td>${{fmt(rr.holdout_pr_auc)}}</td><td>${{fmt(rr.holdout_recall)}}</td><td>${{fmt(rr.time_recall)}}</td><td>${{fmt(rr.delta_recall_hold_minus_time)}}</td></tr>`;
          }});
          html += `</tbody></table>`;
          html += `<div class="small">For deeper breakdowns, see the slice report: <code>${{(ev.slices_report || "reports/eval_slices_login_attempt.md")}}</code></div>`;
        }} else {{
          html += `<div class="small"><span class="warn">Diagnostics not found</span> — run may have skipped evaluation or artifacts are missing.</div>`;
        }}
        if (ev.stability_report) {{
          html += `<div class="small">Stability report path: <code>${{ev.stability_report}}</code></div>`;
        }}
        diag.innerHTML = html;
        card.appendChild(diag);
      }}

      // Notes
      if (r.notes && r.notes.length) {{
        const n = document.createElement("div");
        n.className = "small";
        n.style.marginTop = "10px";
        n.innerHTML = `<b>Notes:</b><ul>${{r.notes.map(x => `<li>${{x}}</li>`).join("")}}</ul>`;
        card.appendChild(n);
      }}

      content.appendChild(card);
    }});
  }}

  metricSel.addEventListener("change", render);
  detailSel.addEventListener("change", render);
  render();
}})();
"""
    # Write outputs
    index_path.write_text(index_html, encoding="utf-8")
    css_path.write_text(css, encoding="utf-8")
    app_path.write_text(app_js, encoding="utf-8")

    # Add small readme
    (out_dir/"README.txt").write_text(
        "Inkswarm DetectLab — MVP Results Viewer\n\n"
        "Open index.html in a browser.\n"
        "This bundle is self-contained (no server required).\n",
        encoding="utf-8"
    )

    return out_dir
