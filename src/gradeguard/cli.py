from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .checks import inspect
from .config import ConfigError, load_config
from .report import terminal_report, write_html


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        prog="gradeguard", description="Check whether a programming assignment is ready to submit."
    )
    command.add_argument("project", nargs="?", default=".", help="project directory (default: current directory)")
    command.add_argument("--config", default="gradeguard.yml", help="config filename or path")
    command.add_argument("--html", nargs="?", const="gradeguard-report.html",
                         help="write an HTML report (default: gradeguard-report.html)")
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        print(f"gradeguard: project directory not found: {project}", file=sys.stderr)
        return 2
    config_path = Path(args.config).expanduser()
    if not config_path.is_absolute():
        config_path = project / config_path
    try:
        config = load_config(config_path)
    except ConfigError as exc:
        print(f"gradeguard: {exc}", file=sys.stderr)
        return 2

    result = inspect(project, config)
    print(terminal_report(result))
    if args.html:
        destination = Path(args.html).expanduser().resolve()
        write_html(result, destination)
        print(f"\nHTML report: {destination}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

