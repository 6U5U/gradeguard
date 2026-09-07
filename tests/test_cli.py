from pathlib import Path

from gradeguard.cli import main


def test_cli_returns_failure_for_missing_required_file(tmp_path: Path, capsys):
    (tmp_path / "gradeguard.yml").write_text("required_files:\n  - README.md\n", encoding="utf-8")
    assert main([str(tmp_path)]) == 1
    assert "NOT READY TO SUBMIT" in capsys.readouterr().out


def test_cli_writes_html_report(tmp_path: Path):
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")
    (tmp_path / "gradeguard.yml").write_text("required_files:\n  - README.md\n", encoding="utf-8")
    output = tmp_path / "report.html"
    assert main([str(tmp_path), "--html", str(output)]) == 0
    assert "Ready to submit" in output.read_text(encoding="utf-8")

