from __future__ import annotations

import fnmatch
import re
import shlex
import subprocess
from pathlib import Path

from .config import Config
from .models import Finding, Report, Status


def _matches(path: Path, patterns: tuple[str, ...]) -> bool:
    value = path.as_posix()
    return any(
        fnmatch.fnmatch(value, pattern)
        or (pattern.startswith("**/") and fnmatch.fnmatch(value, pattern[3:]))
        for pattern in patterns
    )


def source_files(project: Path, config: Config):
    for path in project.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(project)
        if _matches(relative, config.exclude):
            continue
        if _matches(relative, config.include):
            yield path


def check_required_files(project: Path, config: Config) -> list[Finding]:
    findings = []
    for name in config.required_files:
        exists = (project / name).is_file()
        findings.append(Finding("required-files", Status.PASS if exists else Status.FAIL,
                                f"{name} is present" if exists else f"Missing required file: {name}",
                                Path(name)))
    return findings


def check_patterns(project: Path, config: Config) -> list[Finding]:
    findings = []
    compiled: list[tuple[str, re.Pattern[str]]] = []
    for pattern in config.forbidden_patterns:
        try:
            compiled.append((pattern, re.compile(pattern)))
        except re.error as exc:
            findings.append(Finding("forbidden-patterns", Status.FAIL,
                                    f"Invalid regular expression {pattern!r}: {exc}"))
    matches = 0
    for path in source_files(project, config):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            continue
        for number, line in enumerate(lines, 1):
            for label, regex in compiled:
                if regex.search(line):
                    matches += 1
                    findings.append(Finding("forbidden-patterns", Status.FAIL,
                                            f"Matched {label!r}", path.relative_to(project), number))
    if compiled and matches == 0:
        findings.append(Finding("forbidden-patterns", Status.PASS, "No forbidden patterns found"))
    return findings


def check_file_sizes(project: Path, config: Config) -> list[Finding]:
    limit = config.max_file_size_kb * 1024
    oversized = []
    for path in project.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(project)
        if _matches(relative, config.exclude):
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > limit:
            oversized.append(Finding("file-size", Status.WARN,
                                     f"File is {size / 1024:.1f} KB (limit: {config.max_file_size_kb} KB)",
                                     relative))
    return oversized or [Finding("file-size", Status.PASS, "No oversized files found")]


def run_tests(project: Path, config: Config) -> tuple[list[Finding], str]:
    test_config = config.tests
    if not test_config.command:
        return [Finding("tests", Status.WARN, "No test command configured")], ""
    try:
        command = shlex.split(test_config.command)
        completed = subprocess.run(command, cwd=project, capture_output=True, text=True,
                                   timeout=test_config.timeout_seconds, check=False)
    except ValueError as exc:
        return [Finding("tests", Status.FAIL, f"Invalid test command: {exc}")], ""
    except FileNotFoundError:
        return [Finding("tests", Status.FAIL, f"Command not found: {command[0]}")], ""
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + (exc.stderr or "")
        return [Finding("tests", Status.FAIL,
                        f"Tests exceeded {test_config.timeout_seconds} seconds")], output

    output = (completed.stdout or "") + (completed.stderr or "")
    findings = [Finding("tests", Status.PASS if completed.returncode == 0 else Status.FAIL,
                        "Test command passed" if completed.returncode == 0
                        else f"Test command exited with status {completed.returncode}")]
    if test_config.minimum_count:
        count = _test_count(output)
        findings.append(Finding("test-count", Status.PASS if count >= test_config.minimum_count else Status.FAIL,
                                f"Detected {count} tests (minimum: {test_config.minimum_count})"))
    return findings, output


def _test_count(output: str) -> int:
    patterns = (
        r"(\d+) passed",
        r"Ran (\d+) tests?",
        r"Tests run: (\d+)",
        r"Tests:\s+(\d+) passed",
    )
    values = [int(match.group(1)) for pattern in patterns
              for match in re.finditer(pattern, output, re.IGNORECASE)]
    return max(values, default=0)


def inspect(project: Path, config: Config) -> Report:
    report = Report(project=project)
    report.findings.extend(check_required_files(project, config))
    report.findings.extend(check_patterns(project, config))
    report.findings.extend(check_file_sizes(project, config))
    test_findings, output = run_tests(project, config)
    report.findings.extend(test_findings)
    report.tests_output = output
    return report
