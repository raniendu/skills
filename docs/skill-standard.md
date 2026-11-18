# Skill standard

This is the normative standard for this repository. **MUST** is a review
requirement; **SHOULD** is the default unless a contribution documents a reason
to depart. The [Agent Skills specification](https://agentskills.io/specification)
is the format baseline. Rules below deliberately narrow it for portability.

## Scope and structure

A skill MUST solve one bounded, reusable task grounded in demonstrated expertise.
Its canonical directory MUST be `skills/<name>/`, directly under `skills/`.

```text
skills/<name>/
  SKILL.md                 Routing metadata and core instructions
  TESTING.md               Cases, execution evidence, and limitations
  scripts/                 Optional deterministic helpers
  references/              Optional task-specific reference material
  assets/                  Optional templates and synthetic fixtures
```

Only `SKILL.md` and `TESTING.md` are required by this repository. Use supporting
directories only when needed. Scripts and resources MUST be contained within the
skill directory; no symlinks or references to a sibling skill's private files.
Avoid duplicate workflows and undeclared shared runtime dependencies.

## Frontmatter

`SKILL.md` MUST begin with `---` YAML frontmatter and a Markdown body. Use UTF-8.
Names MUST match the parent directory, contain 1-64 ASCII lowercase letters,
digits, or hyphens, and have no leading, trailing, or consecutive hyphens.

Required fields:

- `name`: stable, task-oriented identifier; changing it is a breaking change.
- `description`: 1-1024 characters explaining both the capability and when it
  applies. Include specific trigger language; do not claim universal relevance.
- `license`: a non-empty license identifier or a bundled license-file reference.
  Use `MIT` for original contributions; retain valid upstream terms for ports.
- `metadata`: a mapping of string keys to string values containing `author`,
  `portability`, and `status` as defined below.

Repository metadata:

- `author`: the accountable person or organization, not a fabricated identity.
- `portability`: `portable` or `agent-specific`. Portable means the core workflow
  does not depend on one agent's private tool API; it does not mean every agent
  has been tested. Specific command-line utilities may still be dependencies.
- `status`: `experimental` or `stable`. Start experimental. Stable requires the
  behavioral evidence and cross-agent execution described in the testing guide.

Quote metadata values to preserve their string type. Additional metadata MUST
have a documented purpose. Do not invent top-level fields.

Optional specification fields:

- `compatibility`: 1-500 characters describing actual runtime, platform, package,
  network, or service requirements. Required here when the environment is not
  otherwise generic, and for all `agent-specific` skills.
- `allowed-tools`: experimental and implementation-dependent. Omit for portable
  skills. It MAY appear on an explicitly agent-specific skill if its limitations
  are documented. It is not a portable permission grant.

Fields such as a harness-specific `disable-model-invocation` MUST NOT be added
to portable frontmatter. Do not depend on consumers accepting unknown fields.
See [the template](skill-template.md) for a copyable example.

## Core instructions

Each skill MUST have these level-two sections, with substantive content:

1. **When to use**: positive triggers, non-goals, and cases that should not match.
2. **Inputs and prerequisites**: input/output contracts, dependencies, supported
   versions, authentication mechanism, working directory, and side effects.
3. **Workflow**: actionable steps, decisions, conditional reference loading, and
   consent gates before side effects. Distinguish observation from mutation.
4. **Validation**: checks for the actual output, expected success conditions, and
   evidence to report. Do not equate a completed command with task success.
5. **Failure and recovery**: expected failures, safe stop conditions, retry limits,
   and recovery or rollback guidance. Do not hide errors with a silent fallback.
6. **Safety and limitations**: trust boundaries, privacy, costs, permissions,
   unsupported cases, and explicit approval requirements.
7. **Examples**: at least one realistic synthetic input and expected output or
   artifact. No live credentials, personal data, or unverified success claims.

Use direct instructions and useful domain detail, not generic advice. Prefer
capability language such as "read the file" over an internal tool identifier.
Do not include hidden reasoning requests or instructions to ignore higher-level
policy, disable safeguards, or change the user's agent configuration.

`SKILL.md` MUST stay under 500 lines; aim for fewer than 5,000 tokens. Move detail
into focused references and state when each is needed. The line budget is checked
automatically; the token target and instruction quality require human review.

## Paths, scripts, and dependencies

Resolve bundled paths relative to the skill directory provided by the consuming
agent, never the user's current working directory. Use relative Markdown links
for bundled resources. State when an output path is relative to a user's project
instead. Do not embed personal absolute paths, account IDs, or private hosts.

Scripts MUST validate inputs, give actionable errors, return nonzero on failure,
and avoid leaking sensitive content. Specify timeouts for network operations and
bounded retries where appropriate. Mutating workflows MUST describe idempotency,
preview behavior, confirmation, and recovery limits. Do not promise rollback
where none exists.

Declare language/runtime versions and installation prerequisites. Do not assume
root privileges, an installed MCP server, network access, a provider account, or
unlimited paid inference. Do not install dependencies without authorization.
Treat scripts as executable code requiring independent review and focused tests.

### Portable Python helpers

Every `.py` file under a skill's `scripts/` directory MUST contain exactly one
well-formed [PEP 723 inline script metadata][pep723] block. It MUST declare a
valid `requires-python` version specifier and a `dependencies` array listing all
third-party runtime dependencies as valid Python dependency specifiers. Use
`dependencies = []` for standard-library-only helpers. Do not rely on globally
installed packages, an activated virtual environment, manual `pip install`, or
the repository's root maintenance environment.

For example, a standard-library-only helper can begin with:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
```

`SKILL.md` MUST declare uv as a prerequisite and document execution with
`uv run <skill-directory>/scripts/helper.py`, replacing `<skill-directory>` with
the resolved skill root supplied by the consuming agent. Do not assume its
working directory. Explain any Python/package downloads, network access, and
cache requirements, plus failure behavior when uv or dependencies are
unavailable. Required approval MUST precede installing uv, downloading Python,
or resolving/installing packages; `uv run` may do the latter automatically.
See [uv's script guide][uv-scripts] for execution and metadata details.

This rule is stricter than the metadata specification: both fields are required
here, even for helpers without third-party dependencies. It applies to bundled
skill helpers, not the repository's own maintenance project. There are no
existing skills to migrate when introducing this rule.

[pep723]: https://packaging.python.org/en/latest/specifications/inline-script-metadata/
[uv-scripts]: https://docs.astral.sh/uv/guides/scripts/

## Licensing and maintenance

Follow [the porting guide](porting.md) for borrowed content and upstream tracking.
A reference URL does not grant a copying license. Keep required notices with the
skill so installation does not detach them from the imported material.

Use Git commits as the initial version boundary; there is no required per-skill
version field or release automation. Changes to identifiers, inputs, outputs,
dependencies, permissions, or supported agents MUST identify their compatibility
impact in the PR and update test evidence. Adding a skill does not authorize its
installation, a release, or a live run.

## Enforcement boundary

The repository validator checks layout, the reference format validator, local
metadata policy, required headings, the line budget, non-empty test evidence
files, and bundled Python helpers' inline metadata syntax and field types. It
cannot prove that dependency/version specifiers resolve, all imports are
covered, or documented commands use uv; those require review and focused tests.
CI also runs tooling tests, Python lint/format checks, and Markdown lint.
These checks cannot establish correctness, licensing permission, absence of
secrets, successful agent routing, or safety. Those remain mandatory review and
behavioral-evaluation gates in [the testing guide](testing.md).
