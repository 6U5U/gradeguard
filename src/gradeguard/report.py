from __future__ import annotations

import html
from pathlib import Path

from .models import Report, Status


SYMBOLS = {Status.PASS: "✓", Status.WARN: "!", Status.FAIL: "✗"}


def terminal_report(report: Report) -> str:
    lines = [f"GradeGuard — {report.project}", ""]
    for finding in report.findings:
        location = ""
        if finding.path:
            location = f" ({finding.path}{':' + str(finding.line) if finding.line else ''})"
        lines.append(f"{SYMBOLS[finding.status]} {finding.message}{location}")
    counts = report.counts
    lines.extend(["", f"{counts[Status.PASS]} passed, {counts[Status.WARN]} warnings, "
                       f"{counts[Status.FAIL]} failed",
                  "READY TO SUBMIT" if report.passed else "NOT READY TO SUBMIT"])
    return "\n".join(lines)


def write_html(report: Report, destination: Path) -> None:
    rows = []
    for item in report.findings:
        location = ""
        if item.path:
            location = f"{item.path}{':' + str(item.line) if item.line else ''}"
        rows.append(
            f'<tr class="{item.status.value}"><td>{SYMBOLS[item.status]}</td>'
            f"<td>{html.escape(item.check)}</td><td>{html.escape(item.message)}</td>"
            f"<td>{html.escape(location)}</td></tr>"
        )
    counts = report.counts
    title = "Ready to submit" if report.passed else "Not ready to submit"
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>GradeGuard report</title><style>
body{{font:16px system-ui;max-width:960px;margin:48px auto;padding:0 20px;color:#172033}}
h1{{margin-bottom:4px}} .summary{{color:#566079;margin-bottom:28px}}
table{{width:100%;border-collapse:collapse}}th,td{{padding:12px;text-align:left;border-bottom:1px solid #ddd}}
.pass td:first-child{{color:#16803c}}.warn td:first-child{{color:#a56300}}.fail td:first-child{{color:#c52433}}
pre{{background:#f4f6f8;padding:16px;overflow:auto;border-radius:8px}}
</style></head><body><h1>{html.escape(title)}</h1>
<p class="summary">{counts[Status.PASS]} passed · {counts[Status.WARN]} warnings · {counts[Status.FAIL]} failed</p>
<table><thead><tr><th></th><th>Check</th><th>Result</th><th>Location</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
{f'<h2>Test output</h2><pre>{html.escape(report.tests_output)}</pre>' if report.tests_output else ''}
</body></html>"""
    destination.write_text(document, encoding="utf-8")

