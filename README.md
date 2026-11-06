# raniendu/skills

A shared library of reusable [Agent Skills](https://agentskills.io/specification)
for multiple coding agents.

**Status: repository skeleton only. No skills are included yet.**

The portable unit is a directory containing `SKILL.md` and any supporting files.
Instructions describe capabilities and outcomes, not a particular agent's tool
API. Environment requirements and agent-specific exceptions must be explicit.

## Repository layout

```text
AGENTS.md                    Instructions for agents contributing here
CONTRIBUTING.md              Human and agent contribution workflow
SECURITY.md                  Trust boundaries and vulnerability reporting
docs/
  skill-standard.md          Normative authoring and packaging rules
  skill-template.md          Copyable example, not an installable skill
  porting.md                 Portability, provenance, and licensing checklist
  testing.md                 Validation, evaluations, and review gates
skills/                      Future installable skills; currently none
scripts/validate.py          Structural and repository-policy checks
tests/                       Tests for the repository validator
.github/                     CI and pull request checklist
```

## Start here

- **Writing or changing a skill:** read [AGENTS.md](AGENTS.md), then
  [CONTRIBUTING.md](CONTRIBUTING.md) and the
  [skill standard](docs/skill-standard.md).
- **Porting an existing skill:** also follow [the porting guide](docs/porting.md).
- **Reviewing a contribution:** use [the testing guide](docs/testing.md) and
  [the PR checklist](.github/pull_request_template.md).
- **Consuming a future skill:** inspect its instructions, scripts, license,
  dependencies, and test evidence before enabling it.

## Local checks

Install [uv](https://docs.astral.sh/uv/) and use Python 3.11 or newer:

```sh
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pymarkdown scan --recurse --respect-gitignore .
uv run --locked python -m unittest discover -s tests -v
uv run --locked python scripts/validate.py
```

CI runs the same checks. The validator explicitly reports when it finds no
skills; that result verifies the skeleton, not skill quality or agent support.

## Installation and compatibility

There is nothing to install yet. This repository does not change any agent's
settings, and no npm or Python distribution is published.

Future skills live at `skills/<name>/`. Install or configure those directories
using the consuming agent's documented skill discovery mechanism. Review a
specific Git commit or release before use; prefer a pinned revision for
reproducible environments. Do not load the entire checkout as instructions or
assume every agent supports the same metadata, commands, or permissions.

See [portability requirements](docs/porting.md#compatibility-and-installation).
We claim format compatibility, not tested runtime compatibility, until the
individual skill's `TESTING.md` records actual execution evidence.

## License

Original repository content is [MIT licensed](LICENSE). Imported material must
retain its applicable license and attribution; the root license cannot relicense
third-party work. See [the porting guide](docs/porting.md#provenance-and-license).
