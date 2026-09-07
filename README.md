# GradeGuard

GradeGuard is a local pre-submission checker for programming assignments. It turns a small
rubric file into a repeatable readiness report—before a missing file, forgotten debug print,
or failing test costs points.

## What it checks

- required files from the assignment rubric;
- forbidden patterns such as `TODO` or debug statements;
- unexpectedly large files;
- your project's real test command and minimum expected test count;
- a terminal summary and optional standalone HTML report.

GradeGuard reads source code locally. It does not upload assignments or require an account.

## Install

GradeGuard requires Python 3.10 or newer.

```bash
git clone https://github.com/6U5U/gradeguard.git
cd gradeguard
python -m pip install -e .
```

## Use it on an assignment

Copy [`gradeguard.example.yml`](gradeguard.example.yml) into the assignment repository as
`gradeguard.yml`, then edit it to match the rubric.

```bash
gradeguard /path/to/assignment
gradeguard /path/to/assignment --html
```

GradeGuard exits with status `0` when no checks fail, `1` when the assignment is not ready,
and `2` when the command or configuration is invalid. This makes it suitable for Git hooks
and CI pipelines as well as manual checks.

## Configuration

```yaml
required_files:
  - README.md
  - src/main.py

forbidden_patterns:
  - "\\bTODO\\b"
  - "print\\("

include:
  - "**/*.py"

tests:
  command: "python -m pytest -q"
  timeout_seconds: 120
  minimum_count: 5
```

Forbidden patterns are regular expressions. The test command is split into arguments and
executed directly inside the assignment directory; shell expansion and pipelines are not
enabled.

## Develop

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
```

## Roadmap

- language adapters for Python, Java, C, and C++;
- Git hygiene and accidental-secret checks;
- rubric scoring and weighted requirements;
- machine-readable JSON reports;
- a setup wizard that creates `gradeguard.yml`.

## License

[MIT](LICENSE)
