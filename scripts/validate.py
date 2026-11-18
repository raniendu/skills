"""Validate skill structure and local policy without executing skill code."""

from __future__ import annotations

import os
import re
import tomllib
from pathlib import Path

from skills_ref import SkillError, read_properties, validate

REQUIRED_SECTIONS = (
    "When to use",
    "Inputs and prerequisites",
    "Workflow",
    "Validation",
    "Failure and recovery",
    "Safety and limitations",
    "Examples",
)
IGNORED_DIRECTORIES = {".git", ".venv", "__pycache__", ".ruff_cache"}
NAME_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SCRIPT_METADATA_PATTERN = re.compile(
    r"(?m)^# /// script\r?\n((?:#(?: [^\r\n]*)?\r?\n)*?)# ///\r?$"
)


def section_contents(content: str) -> dict[str, list[str]]:
    """Collect level-two sections, ignoring headings inside fenced examples."""
    sections: dict[str, list[str]] = {}
    current: str | None = None
    fence: str | None = None
    for line in content.splitlines():
        stripped = line.strip()
        marker = re.match(r"^(`{3,}|~{3,})", stripped)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            if current is not None:
                sections[current].append(line)
            continue
        if fence is None and line.startswith("## "):
            current = line[3:].strip()
            sections.setdefault(current, [])
        elif current is not None:
            sections[current].append(line)
    return sections


def check_python_script(path: Path) -> list[str]:
    """Check inline metadata without executing code or resolving dependencies."""
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"Cannot read Python script: {exc}"]
    blocks = SCRIPT_METADATA_PATTERN.findall(content)
    if len(blocks) != 1 or content.splitlines().count("# /// script") != 1:
        return ["Python helpers require exactly one well-formed PEP 723 script block"]
    try:
        metadata = tomllib.loads("\n".join(line[2:] for line in blocks[0].splitlines()))
    except tomllib.TOMLDecodeError as exc:
        return [f"Invalid PEP 723 TOML: {exc}"]

    errors: list[str] = []
    requires_python = metadata.get("requires-python")
    if not isinstance(requires_python, str) or not requires_python.strip():
        errors.append("PEP 723 requires-python must be a non-empty string")
    dependencies = metadata.get("dependencies")
    if not isinstance(dependencies, list) or any(
        not isinstance(dependency, str) or not dependency.strip()
        for dependency in dependencies
    ):
        errors.append("PEP 723 dependencies must be an array of non-empty strings")
    return errors


def check_skill(directory: Path) -> list[str]:
    """Apply the reference validator plus this repository's stricter profile."""
    errors: list[str] = []
    skill_file = directory / "SKILL.md"
    if "SKILL.md" not in {path.name for path in directory.iterdir()}:
        return ["Missing required file: SKILL.md (case-sensitive)"]
    if any(path.is_symlink() for path in directory.rglob("*")):
        return ["symlinks are not allowed"]
    if not skill_file.is_file():
        return ["SKILL.md must be a regular file"]
    try:
        errors.extend(validate(directory))
        properties = read_properties(directory)
        content = skill_file.read_text(encoding="utf-8")
    except (SkillError, OSError, UnicodeError, TypeError, ValueError) as exc:
        return [f"Cannot validate skill: {exc}"]

    if not NAME_PATTERN.fullmatch(properties.name):
        errors.append("name must use ASCII lowercase letters, digits, and hyphens")
    if not isinstance(properties.license, str) or not properties.license.strip():
        errors.append("license must be a non-empty string")
    metadata = properties.metadata
    if not isinstance(metadata, dict):
        errors.append("metadata must contain author, portability, and status")
        metadata = {}
    if not isinstance(metadata.get("author"), str) or not metadata["author"].strip():
        errors.append("metadata.author must be a non-empty string")
    portability = metadata.get("portability")
    if portability not in {"portable", "agent-specific"}:
        errors.append("metadata.portability must be portable or agent-specific")
    if metadata.get("status") not in {"experimental", "stable"}:
        errors.append("metadata.status must be experimental or stable")
    if portability == "agent-specific" and not properties.compatibility:
        errors.append("agent-specific skills must declare compatibility")
    if portability == "portable" and properties.allowed_tools is not None:
        errors.append("portable skills must omit experimental allowed-tools")

    if len(content.splitlines()) >= 500:
        errors.append("SKILL.md must contain fewer than 500 lines")
    sections = section_contents(content)
    for heading in REQUIRED_SECTIONS:
        if not any(line.strip() for line in sections.get(heading, [])):
            errors.append(f"Missing or empty section: {heading}")
    evidence = directory / "TESTING.md"
    if not evidence.is_file() or not evidence.read_text(encoding="utf-8").strip():
        errors.append("Missing or empty TESTING.md")
    for script in sorted((directory / "scripts").rglob("*.py")):
        if script.is_file():
            errors.extend(
                f"{script.relative_to(directory)}: {error}"
                for error in check_python_script(script)
            )
    return errors


def check_repository(root: Path) -> tuple[list[str], int]:
    """Check canonical layout and policy, including the intentional empty state."""
    errors: list[str] = []
    count = 0
    catalog = root / "skills"
    if not catalog.is_dir() or catalog.is_symlink():
        return ["skills/ must be a real directory"], 0

    for entry in sorted(catalog.iterdir()):
        if entry.is_symlink():
            errors.append(f"{entry.relative_to(root)}: symlinks are not allowed")
        elif entry.is_dir():
            count += 1
            try:
                skill_errors = check_skill(entry)
            except (OSError, UnicodeError) as exc:
                skill_errors = [f"Cannot read skill files: {exc}"]
            errors.extend(f"{entry.name}: {error}" for error in skill_errors)
        elif entry.name != "README.md":
            errors.append(f"skills/{entry.name}: only README.md and skill dirs allowed")

    for directory, subdirs, files in os.walk(root, followlinks=False):
        subdirs[:] = [name for name in subdirs if name not in IGNORED_DIRECTORIES]
        base = Path(directory)
        for name in subdirs + files:
            path = base / name
            relative = path.relative_to(root)
            if path.is_symlink() and catalog in path.parents:
                errors.append(f"{relative}: symlinks are not allowed")
            if name.lower() == "skill.md":
                if name != "SKILL.md" or len(relative.parts) != 3:
                    errors.append(f"{relative}: use skills/<name>/SKILL.md only")
                elif relative.parts[0] != "skills":
                    errors.append(f"{relative}: skills must be under skills/")
    return errors, count


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors, count = check_repository(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    if count == 0:
        print("Validated repository skeleton: 0 skills (intentionally empty).")
    else:
        print(f"Validated structure and metadata for {count} skill(s).")
    print("Behavior, licensing, privacy, safety, and compatibility need review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
