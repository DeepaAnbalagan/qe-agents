from __future__ import annotations

import html
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .models import WorkflowState


def _esc(value: object) -> str:
    return html.escape(str(value))


def render_html_report(state: WorkflowState) -> str:
    defect = state.triaged_defect
    run = state.test_run
    plan = state.test_plan
    validation = state.validation

    severity = _esc(defect.severity if defect else "N/A")
    classification = _esc(defect.classification if defect else "N/A")
    confidence = f"{defect.confidence * 100:.0f}%" if defect else "N/A"
    title = _esc(defect.title if defect else "QE Agent Report")

    scenario_rows = "".join(
        f"""
        <tr>
          <td>{_esc(s.id)}</td>
          <td>{_esc(s.title)}</td>
          <td>{_esc(s.type)}</td>
          <td><span class=\"badge risk-{_esc(s.risk.lower())}\">{_esc(s.risk)}</span></td>
          <td>{_esc(s.priority)}</td>
        </tr>
        """
        for s in (plan.scenarios if plan else [])
    )

    attempt_rows = "".join(
        f"""
        <tr>
          <td>{a.attempt}</td>
          <td>{a.exit_code}</td>
          <td><span class=\"badge\">{_esc('PASS' if a.exit_code == 0 else 'FAIL')}</span></td>
          <td><pre>{_esc(a.stderr[-1500:] if a.stderr else a.stdout[-1500:])}</pre></td>
        </tr>
        """
        for a in (run.attempts if run else [])
    )

    evidence = "".join(f"<li>{_esc(item)}</li>" for item in (defect.evidence if defect else []))
    ambiguities = "".join(f"<li>{_esc(item)}</li>" for item in (plan.ambiguities if plan else []))
    validation_errors = "".join(f"<li>{_esc(item)}</li>" for item in (validation.errors if validation else []))

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>QE Agents Report - {title}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif; margin: 0; background: #f5f7fb; color: #172033; }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 32px; }}
  .header {{ background: white; border-radius: 14px; padding: 24px; box-shadow: 0 2px 10px rgba(0,0,0,.06); }}
  h1 {{ margin: 0 0 8px; font-size: 28px; }}
  h2 {{ margin-top: 0; }}
  .muted {{ color: #667085; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin: 20px 0; }}
  .card {{ background: white; border-radius: 12px; padding: 18px; box-shadow: 0 2px 10px rgba(0,0,0,.05); }}
  .metric {{ font-size: 24px; font-weight: 700; margin-top: 6px; }}
  .section {{ background: white; border-radius: 12px; padding: 22px; margin-top: 18px; box-shadow: 0 2px 10px rgba(0,0,0,.05); }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
  th, td {{ border-bottom: 1px solid #eaecf0; padding: 10px; text-align: left; vertical-align: top; }}
  th {{ font-size: 13px; color: #667085; }}
  .badge {{ display: inline-block; padding: 4px 8px; border-radius: 999px; background: #eef2f6; font-size: 12px; font-weight: 600; }}
  .risk-critical {{ background: #fee4e2; }}
  .risk-high {{ background: #ffefd5; }}
  .risk-medium {{ background: #eef4ff; }}
  .risk-low {{ background: #ecfdf3; }}
  pre {{ white-space: pre-wrap; word-break: break-word; margin: 0; font-size: 12px; background: #f8fafc; padding: 10px; border-radius: 8px; }}
  code {{ background: #f2f4f7; padding: 2px 5px; border-radius: 4px; }}
  @media print {{ body {{ background: white; }} .container {{ max-width: none; }} .card, .section, .header {{ box-shadow: none; border: 1px solid #ddd; }} }}
</style>
</head>
<body>
<div class=\"container\">
  <div class=\"header\">
    <div class=\"muted\">QE Agents • Triage Report</div>
    <h1>{title}</h1>
    <div class=\"muted\">Workflow { _esc(state.workflow_id) } • Generated {generated_at}</div>
  </div>

  <div class=\"grid\">
    <div class=\"card\"><div class=\"muted\">Classification</div><div class=\"metric\">{classification}</div></div>
    <div class=\"card\"><div class=\"muted\">Severity</div><div class=\"metric\">{severity}</div></div>
    <div class=\"card\"><div class=\"muted\">Confidence</div><div class=\"metric\">{confidence}</div></div>
    <div class=\"card\"><div class=\"muted\">Test Run</div><div class=\"metric\">{_esc(run.final_status if run else 'N/A')}</div></div>
  </div>

  <div class=\"section\">
    <h2>Defect Summary</h2>
    <p><strong>Priority:</strong> {_esc(defect.priority if defect else 'N/A')}</p>
    <p><strong>Likely owner:</strong> {_esc(defect.likely_owner if defect else 'N/A')}</p>
    <p><strong>Root cause:</strong> {_esc(defect.root_cause if defect else 'N/A')}</p>
    <h3>Evidence</h3>
    <ul>{evidence or '<li>No evidence recorded.</li>'}</ul>
  </div>

  <div class=\"section\">
    <h2>Test Plan</h2>
    <p>{_esc(plan.summary if plan else 'No test plan.')}</p>
    <table>
      <thead><tr><th>ID</th><th>Scenario</th><th>Type</th><th>Risk</th><th>Priority</th></tr></thead>
      <tbody>{scenario_rows or '<tr><td colspan=\"5\">No scenarios.</td></tr>'}</tbody>
    </table>
    <h3>Ambiguities</h3>
    <ul>{ambiguities or '<li>None identified.</li>'}</ul>
  </div>

  <div class=\"section\">
    <h2>Validation</h2>
    <p><strong>Status:</strong> {_esc('VALID' if validation and validation.valid else 'INVALID')}</p>
    <ul>{validation_errors or '<li>No validation errors.</li>'}</ul>
  </div>

  <div class=\"section\">
    <h2>Execution Attempts</h2>
    <table>
      <thead><tr><th>Attempt</th><th>Exit Code</th><th>Status</th><th>Evidence</th></tr></thead>
      <tbody>{attempt_rows or '<tr><td colspan=\"4\">No execution attempts.</td></tr>'}</tbody>
    </table>
  </div>

  <div class=\"section\">
    <h2>Workflow Audit</h2>
    <p><code>{_esc(' → '.join(state.audit_log))}</code></p>
  </div>
</div>
</body>
</html>
"""


def write_html_report(state: WorkflowState, output_dir: str = "reports") -> Path:
    report_dir = Path(output_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"qe-report-{state.workflow_id}.html"
    path.write_text(render_html_report(state), encoding="utf-8")
    return path
