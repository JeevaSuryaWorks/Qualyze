from datetime import datetime, timezone
import html
import json

def build_html_report(source_name, report):
    summary = report["summary"]
    findings = report["findings"]
    rows = []
    for f in findings:
        sev = f["severity"].lower()
        badge_class = f"badge-{sev}"
        rows.append(
            f"""<tr>
                <td><span class="badge {badge_class}">{html.escape(f['severity'])}</span></td>
                <td><code>{html.escape(f['rule_id'])}</code></td>
                <td><b>{html.escape(f['title'])}</b><br><small style="color:#64748b">{html.escape(f['description'])}</small></td>
                <td><span class="affected-tag">{html.escape(str(f['affected']))}</span></td>
                <td>{html.escape(f['recommendation'])}</td>
            </tr>"""
        )
    findings_html = "".join(rows) or '<tr><td colspan="5" style="text-align:center;padding:24px;color:#64748b;">No quality or leakage findings detected.</td></tr>'
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    score = summary['quality_score']
    score_color = "#10b981" if score >= 85 else ("#f59e0b" if score >= 60 else "#ef4444")
    
    column_rows = []
    for _, r in report['column_profile'].iterrows():
        pct = r['missing_pct']
        pct_color = "#ef4444" if pct > 15 else ("#f59e0b" if pct > 0 else "#10b981")
        column_rows.append(
            f"""<tr>
                <td><b>{html.escape(str(r['column']))}</b></td>
                <td><span class="type-pill">{html.escape(str(r['inferred_type']))}</span></td>
                <td>{r['missing_count']}</td>
                <td><span style="color:{pct_color};font-weight:600">{pct}%</span></td>
                <td>{r['unique_values']}</td>
            </tr>"""
        )
    col_profile_html = "".join(column_rows)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DataSentinel — Dataset Audit Report: {html.escape(str(source_name))}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0b0f19;
    --card: #131b2e;
    --card-border: rgba(255, 255, 255, 0.08);
    --text: #f8fafc;
    --text-muted: #94a3b8;
    --accent: #6366f1;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #0b0f19;
    color: var(--text);
    padding: 40px 24px;
    line-height: 1.6;
  }}
  .container {{ max-width: 1200px; margin: 0 auto; }}
  .header {{
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 32px;
    margin-bottom: 28px;
    backdrop-filter: blur(12px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  }}
  .badge-tag {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #38bdf8;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.25);
    padding: 4px 10px;
    border-radius: 9999px;
    margin-bottom: 12px;
  }}
  h1 {{
    font-size: 28px;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
  }}
  .meta {{ color: var(--text-muted); font-size: 14px; display: flex; gap: 24px; flex-wrap: wrap; margin-top: 10px; }}
  .meta b {{ color: #cbd5e1; }}
  .cards {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin-bottom: 32px;
  }}
  .card {{
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 22px;
    transition: transform 0.2s ease;
  }}
  .card-label {{ font-size: 13px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }}
  .card-value {{ font-size: 32px; font-weight: 800; color: #fff; margin-top: 6px; }}
  .section-title {{
    font-size: 20px;
    font-weight: 700;
    color: #fff;
    margin: 36px 0 16px 0;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 24px;
  }}
  th, td {{
    padding: 14px 18px;
    text-align: left;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    font-size: 14px;
  }}
  th {{
    background: rgba(255, 255, 255, 0.03);
    color: var(--text-muted);
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
  }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: rgba(255, 255, 255, 0.02); }}
  .badge {{
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  .badge-high {{ background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }}
  .badge-medium {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }}
  .badge-low {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }}
  .type-pill {{
    display: inline-block;
    background: rgba(99, 102, 241, 0.12);
    color: #a5b4fc;
    border: 1px solid rgba(99, 102, 241, 0.25);
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 12px;
  }}
  .affected-tag {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    background: rgba(255, 255, 255, 0.06);
    padding: 3px 8px;
    border-radius: 6px;
  }}
  code {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    background: rgba(255, 255, 255, 0.08);
    padding: 2px 6px;
    border-radius: 4px;
    color: #38bdf8;
  }}
  .callout {{
    background: rgba(99, 102, 241, 0.08);
    border-left: 4px solid #6366f1;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 20px 0;
    font-size: 13px;
    color: #cbd5e1;
  }}
  footer {{
    text-align: center;
    color: var(--text-muted);
    font-size: 12px;
    margin-top: 48px;
    padding-top: 24px;
    border-top: 1px solid var(--card-border);
  }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="badge-tag">🛡️ DataSentinel Security & Quality Audit</div>
    <h1>Dataset Audit & Readiness Report</h1>
    <div class="meta">
      <div><b>Source File:</b> {html.escape(str(source_name))}</div>
      <div><b>Generated:</b> {html.escape(generated)}</div>
      <div><b>Engine:</b> Autonomous Heuristic Profiler v1.2</div>
    </div>
  </div>

  <div class="cards">
    <div class="card">
      <div class="card-label">Total Rows</div>
      <div class="card-value">{summary['rows']:,}</div>
    </div>
    <div class="card">
      <div class="card-label">Total Columns</div>
      <div class="card-value">{summary['columns']:,}</div>
    </div>
    <div class="card">
      <div class="card-label">Flagged Findings</div>
      <div class="card-value" style="color: {'#ef4444' if summary['finding_count'] > 0 else '#10b981'}">{summary['finding_count']}</div>
    </div>
    <div class="card">
      <div class="card-label">Health Score</div>
      <div class="card-value" style="color: {score_color}">{score} <span style="font-size:16px;color:var(--text-muted)">/100</span></div>
    </div>
  </div>

  <div class="callout">
    💡 <b>Governance Note:</b> Quality score reflects a transparent heuristic assessment across completeness, redundancy, and target association. Findings represent algorithmic risk flags for data scientists and ML engineers, not certified proof of dataset invalidity.
  </div>

  <h2 class="section-title">🛡️ Identified Quality & ML Readiness Findings</h2>
  <table>
    <thead>
      <tr><th>Severity</th><th>Rule</th><th>Finding & Context</th><th>Affected Scope</th><th>Recommended Action</th></tr>
    </thead>
    <tbody>{findings_html}</tbody>
  </table>

  <h2 class="section-title">📊 Column-Level Profiling Matrix</h2>
  <table>
    <thead>
      <tr><th>Column Name</th><th>Inferred Type</th><th>Missing Count</th><th>Missing %</th><th>Unique Values</th></tr>
    </thead>
    <tbody>{col_profile_html}</tbody>
  </table>

  <footer>
    Generated autonomously by DataSentinel — Modern ML Dataset Governance & Profiling
  </footer>
</div>
</body>
</html>"""
