from pathlib import Path

import pytest

from gradeguard.config import ConfigError, load_config


def test_loads_minimal_config(tmp_path: Path):
    path = tmp_path / "gradeguard.yml"
    path.write_text("required_files:\n  - README.md\n", encoding="utf-8")
    config = load_config(path)
    assert config.required_files == ("README.md",)
    assert config.tests.timeout_seconds == 120


def test_rejects_invalid_required_files(tmp_path: Path):
    path = tmp_path / "gradeguard.yml"
    path.write_text("required_files: README.md\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="list of strings"):
        load_config(path)

