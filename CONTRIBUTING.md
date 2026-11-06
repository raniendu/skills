# Contributing

Humans and agents use the same standards. Read [AGENTS.md](AGENTS.md) and the
[normative skill standard](docs/skill-standard.md) before starting.

## Scope

A skill should capture reusable, demonstrated expertise for a bounded task.
Do not add generic advice the model already knows, a collection of unrelated
workflows, a snapshot of personal agent configuration, or a wrapper that exists
only to redirect to another copy of the same skill.

This repository starts with no skills. Additions require an explicit request;
do not seed a collection by copying locally installed skills.

## Workflow

1. Inspect existing changes and create a focused branch from the current default
   branch. Preserve work that is not yours.
2. Check for overlap with existing skills. Explain the task, intended triggers,
   non-goals, dependencies, side effects, and intended users.
3. For an import, establish provenance and license permissions **before** copying.
   Follow [the porting checklist](docs/porting.md).
4. Create `skills/<name>/` using the example in
   [the template guide](docs/skill-template.md). Add only needed support files.
5. Write routing, workflow, safety, recovery, examples, and verification guidance.
   Add `TESTING.md` and safe fixtures or automated tests where useful.
6. Run [repository checks and behavioral evaluations](docs/testing.md). Test from
   outside the skill directory so working-directory assumptions are visible.
7. Review the entire diff, including scripts, dependencies, lockfile changes,
   bundled assets, and licenses. Confirm no private or generated data is present.
8. Open a pull request with the checklist and actual evidence. State anything
   untested. Obtain maintainer review before merging.

## Standards changes

Update documentation, validator behavior, and validator tests together. Explain
why a stricter rule is needed and its effect on existing skills. Do not loosen a
rule solely to make one contribution pass. Review upstream specification changes
explicitly instead of automatically adopting new agent-specific fields.

## Dependencies and generated files

Repository maintenance uses `uv`; `uv.lock` is committed. Use `uv sync --locked`
for normal checks. When intentionally changing development dependencies, update
`pyproject.toml` and regenerate the lockfile with `uv lock`, then review both.

The root Python project is validation tooling only, not a runtime dependency for
installed skills. Declare each skill's runtime requirements in that skill.
Do not add global setup, install hooks, credentials, or a shared runtime merely
for convenience. Keep generated evaluation outputs and local environments out
of Git.

## Licensing

Contributions must be original MIT-compatible work or have documented permission
and preserved terms. Do not assume public code is licensed for reuse. A source
with no license is not an acceptable import without separate permission.
See [provenance and license](docs/porting.md#provenance-and-license).
