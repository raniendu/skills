# Testing and review

Skill format, instruction quality, and runtime behavior are different checks.
Passing one does not imply the others passed.

## Repository checks

Run from the repository root with Python 3.11+ and uv:

```sh
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pymarkdown scan --recurse --respect-gitignore .
uv run --locked python -m unittest discover -s tests -v
uv run --locked python scripts/validate.py
```

The Python project is maintainer tooling only. `uv.lock` pins the dependency
resolution. Normal checks must not change dependencies or need API credentials.
Dependency installation needs network access; the checks themselves use local,
synthetic inputs. Root CI must not automatically run newly contributed skill
scripts or make model calls.

`scripts/validate.py` uses `skills-ref` for format validation and enforces the
local policy in [the standard](skill-standard.md). For each bundled Python helper
under `scripts/`, it requires one well-formed PEP 723 block, parses its TOML, and
checks the required `requires-python` and `dependencies` field types. Offline
regression tests cover third-party and standard-library-only declarations,
missing/malformed/duplicate blocks, invalid fields, nested helpers, and encoding
failures without executing scripts or resolving packages. Reviewers must still
check specifier validity, complete dependency declarations, uv commands, and
behavior from an unrelated working directory.

Zero discovered skills is a valid, explicitly reported skeleton state, not
evidence of useful skill behavior. The new Python-helper rule has no existing
skills to migrate; fixture passes do not establish real helper portability.

To inspect one future skill directly with the pinned reference implementation:

```sh
uv run --locked agentskills validate skills/<name>
```

The installed `skills-ref==0.1.1` distribution exposes the `agentskills` command;
upstream documentation may call the executable `skills-ref` instead. The repository
wrapper is the authoritative local entry point for the additional policy checks.

## Required skill evidence

Every skill MUST include a substantive `TESTING.md` with:

- Scope and setup: dependencies, agent and runtime versions, operating system,
  date, candidate revision or working-tree description, and any network/cost.
- Routing cases: at least two prompts that should trigger and two related prompts
  that should not trigger the skill; state expected decisions and actual results.
- Behavior cases: representative successful output and an edge case, with concrete
  expected properties rather than only a subjective quality rating.
- Failure cases: invalid input and a missing dependency or unavailable service,
  with safe expected behavior and no silent permission expansion.
- Safety cases: untrusted input or embedded instructions, sensitive output risk,
  and any applicable side-effect/consent gate.
- Results: actual observations, checks run, artifacts or sanitized evidence,
  unresolved limitations, and an explicit list of cases not run.

Use synthetic fixtures. Never publish credentials, private transcripts, full user
data, or sensitive logs as evidence. Do not turn a guessed result into a pass.
"Not run" is acceptable for experimental work when clearly explained; it is not
execution evidence and cannot satisfy the stable gate.

## Behavioral evaluation

1. Define expected behavior before execution. Keep representative prompts and
   output assertions separate from the instructions under test.
2. Test routing with normal discovery, not only explicit invocation. Also force
   invocation to distinguish routing failures from workflow failures.
3. Run the workflow from an unrelated working directory to catch path assumptions.
4. Exercise dependencies, output validation, recovery, and consent boundaries.
   Test deterministic helpers independently using local fixtures.
5. Record agent/runtime versions and observed outcomes. For model-driven behavior,
   note variation and repeat important failure cases where useful.
6. For a portable skill to become stable, obtain successful evidence on at least
   two distinct agent implementations. Agent-specific stable skills must pass on
   their declared implementation and keep that limitation explicit.

Live, paid, destructive, or production evaluations require the user's explicit
approval of scope, environment, side effects, and any cost before execution.
The skill's presence and a request to run repository checks are not approval.

## Review gate

Reviewers must check:

- [ ] Task value, routing specificity, non-goals, and overlap with existing skills.
- [ ] Portable instructions, declared prerequisites, and honest compatibility.
- [ ] Working bundled paths, no external symlinks, and complete licensed assets.
- [ ] Script correctness, safe input handling, least privilege, and bounded retries.
- [ ] Secrets/privacy review and resistance to untrusted embedded instructions.
- [ ] Explicit side-effect approval gates and realistic recovery limits.
- [ ] Provenance, distribution rights, and required attribution.
- [ ] Actual skill-specific evidence, including limitations and failed cases.
- [ ] Required repository checks and a complete diff review.

Automated checks do not replace these items. If diagnostics or a required check
are unavailable, report exactly what was and was not verified. Do not add blanket
suppressions or weaken a policy to make the contribution appear clean.
