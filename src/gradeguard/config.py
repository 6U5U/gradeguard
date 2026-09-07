from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class TestConfig:
    command: str = ""
    timeout_seconds: int = 120
    minimum_count: int = 0


@dataclass(frozen=True)
class Config:
    required_files: tuple[str, ...] = ()
    forbidden_patterns: tuple[str, ...] = ()
    include: tuple[str, ...] = ("**/*.py", "**/*.java", "**/*.c", "**/*.cpp", "**/*.js", "**/*.ts")
    exclude: tuple[str, ...] = (".git/**", ".venv/**", "venv/**", "node_modules/**", "dist/**", "build/**")
    max_file_size_kb: int = 1024
    tests: TestConfig = field(default_factory=TestConfig)


def _string_list(data: dict[str, Any], key: str) -> tuple[str, ...]:
    value = data.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError(f"'{key}' must be a list of strings")
    return tuple(value)


def load_config(path: Path) -> Config:
    if not path.is_file():
        raise ConfigError(f"configuration file not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ConfigError(f"could not read configuration: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigError("configuration must be a YAML mapping")

    tests_raw = raw.get("tests", {}) or {}
    if not isinstance(tests_raw, dict):
        raise ConfigError("'tests' must be a mapping")
    command = tests_raw.get("command", "")
    timeout = tests_raw.get("timeout_seconds", 120)
    minimum = tests_raw.get("minimum_count", 0)
    if not isinstance(command, str):
        raise ConfigError("'tests.command' must be a string")
    if not isinstance(timeout, int) or timeout < 1:
        raise ConfigError("'tests.timeout_seconds' must be a positive integer")
    if not isinstance(minimum, int) or minimum < 0:
        raise ConfigError("'tests.minimum_count' must be a non-negative integer")

    max_size = raw.get("max_file_size_kb", 1024)
    if not isinstance(max_size, int) or max_size < 1:
        raise ConfigError("'max_file_size_kb' must be a positive integer")

    defaults = Config()
    return Config(
        required_files=_string_list(raw, "required_files"),
        forbidden_patterns=_string_list(raw, "forbidden_patterns"),
        include=_string_list(raw, "include") if "include" in raw else defaults.include,
        exclude=_string_list(raw, "exclude") if "exclude" in raw else defaults.exclude,
        max_file_size_kb=max_size,
        tests=TestConfig(command=command, timeout_seconds=timeout, minimum_count=minimum),
    )

