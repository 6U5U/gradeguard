from pathlib import Path

from gradeguard.checks import _test_count, check_patterns, check_required_files, source_files
from gradeguard.config import Config
from gradeguard.models import Status


def test_required_file_failure(tmp_path: Path):
    findings = check_required_files(tmp_path, Config(required_files=("README.md",)))
    assert findings[0].status == Status.FAIL


def test_forbidden_pattern_reports_line(tmp_path: Path):
    source = tmp_path / "src"
    source.mkdir()
    (source / "main.py").write_text("value = 1\nprint(value)\n", encoding="utf-8")
    findings = check_patterns(tmp_path, Config(forbidden_patterns=(r"print\(",), include=("**/*.py",)))
    assert findings[0].status == Status.FAIL
    assert findings[0].line == 2


def test_test_count_understands_common_runners():
    assert _test_count("7 passed in 0.04s") == 7
    assert _test_count("Ran 12 tests in 1.0s") == 12


def test_recursive_glob_includes_root_level_source(tmp_path: Path):
    root_file = tmp_path / "main.py"
    root_file.write_text("value = 1\n", encoding="utf-8")
    assert list(source_files(tmp_path, Config(include=("**/*.py",)))) == [root_file]
