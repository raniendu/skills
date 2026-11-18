"""Offline regression tests; skill fixtures exist only in temporary directories."""

from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

from scripts.validate import REQUIRED_SECTIONS, check_repository

REPOSITORY = Path(__file__).resolve().parents[1]


def skill_text(name: str = "sample-task") -> str:
    frontmatter = (
        f"---\nname: {name}\n"
        "description: Inspect synthetic input. Use when asked to inspect a sample.\n"
        "license: MIT\nmetadata:\n"
        '  author: "test-author"\n'
        '  portability: "portable"\n'
        '  status: "experimental"\n---\n\n# Sample task\n'
    )
    return frontmatter + "".join(
        f"\n## {heading}\n\nConcrete test instructions.\n"
        for heading in REQUIRED_SECTIONS
    )


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "skills").mkdir()

    def add_skill(self, content: str | None = None) -> Path:
        directory = self.root / "skills" / "sample-task"
        directory.mkdir()
        (directory / "SKILL.md").write_text(
            content if content is not None else skill_text(), encoding="utf-8"
        )
        (directory / "TESTING.md").write_text(
            "# Test evidence\n\nSynthetic fixture; no live calls.\n", encoding="utf-8"
        )
        return directory

    def add_script(self, content: str, name: str = "helper.py") -> Path:
        directory = self.root / "skills" / "sample-task"
        if not directory.exists():
            self.add_skill()
        path = directory / "scripts" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def errors(self) -> str:
        return "\n".join(check_repository(self.root)[0])

    def test_empty_skeleton_is_valid(self) -> None:
        self.assertEqual(check_repository(self.root), ([], 0))

    def test_catalog_directory_is_required(self) -> None:
        (self.root / "skills").rmdir()
        self.assertIn("real directory", self.errors())

    def test_valid_skill(self) -> None:
        self.add_skill()
        self.assertEqual(check_repository(self.root), ([], 1))

    def test_directory_and_name_must_match(self) -> None:
        self.add_skill(skill_text("other-task"))
        self.assertIn("must match skill name", self.errors())

    def test_ascii_name_profile(self) -> None:
        self.add_skill(skill_text("tâche"))
        self.assertIn("ASCII", self.errors())

    def test_reference_rejects_unknown_fields(self) -> None:
        self.add_skill(
            skill_text().replace("license: MIT", "unknown: value\nlicense: MIT")
        )
        self.assertIn("Unexpected fields", self.errors())

    def test_frontmatter_is_required(self) -> None:
        self.add_skill("# No frontmatter\n")
        self.assertIn("frontmatter", self.errors())

    def test_repository_metadata_and_license_are_required(self) -> None:
        for field in (
            "license: MIT\n",
            '  author: "test-author"\n',
            '  portability: "portable"\n',
            '  status: "experimental"\n',
        ):
            with self.subTest(field=field):
                directory = self.root / "skills" / "sample-task"
                if not directory.exists():
                    self.add_skill()
                (directory / "SKILL.md").write_text(
                    skill_text().replace(field, ""), encoding="utf-8"
                )
                self.assertTrue(self.errors())

    def test_metadata_values_are_constrained(self) -> None:
        self.add_skill(skill_text().replace('"experimental"', '"unreviewed"'))
        self.assertIn("metadata.status", self.errors())

    def test_agent_specific_requires_compatibility(self) -> None:
        self.add_skill(skill_text().replace('"portable"', '"agent-specific"'))
        self.assertIn("declare compatibility", self.errors())

    def test_agent_specific_can_declare_tools(self) -> None:
        content = skill_text().replace('"portable"', '"agent-specific"')
        content = content.replace(
            "license: MIT",
            "license: MIT\ncompatibility: Test agent\nallowed-tools: Read",
        )
        self.add_skill(content)
        self.assertEqual(check_repository(self.root), ([], 1))

    def test_portable_rejects_allowed_tools(self) -> None:
        self.add_skill(
            skill_text().replace("license: MIT", "license: MIT\nallowed-tools: Read")
        )
        self.assertIn("omit experimental allowed-tools", self.errors())

    def test_missing_or_empty_sections(self) -> None:
        self.add_skill(
            skill_text().replace("## Workflow\n\nConcrete test instructions.", "")
        )
        self.assertIn("Missing or empty section: Workflow", self.errors())

    def test_fenced_headings_do_not_satisfy_sections(self) -> None:
        self.add_skill(
            skill_text().replace("## Workflow", "```markdown\n## Workflow\n```")
        )
        self.assertIn("Missing or empty section: Workflow", self.errors())

    def test_line_budget(self) -> None:
        self.add_skill(skill_text() + "\n" * 500)
        self.assertIn("fewer than 500 lines", self.errors())

    def test_evidence_is_required(self) -> None:
        directory = self.add_skill()
        (directory / "TESTING.md").unlink()
        self.assertIn("TESTING.md", self.errors())

    def test_empty_evidence_is_rejected(self) -> None:
        directory = self.add_skill()
        (directory / "TESTING.md").write_text("\n", encoding="utf-8")
        self.assertIn("TESTING.md", self.errors())

    def test_invalid_encoding_is_rejected(self) -> None:
        directory = self.add_skill()
        (directory / "SKILL.md").write_bytes(b"\xff")
        self.assertIn("Cannot validate", self.errors())

    def test_nested_skill_is_rejected(self) -> None:
        directory = self.add_skill() / "nested"
        directory.mkdir()
        (directory / "SKILL.md").write_text(skill_text(), encoding="utf-8")
        self.assertIn("skills/<name>/SKILL.md only", self.errors())

    def test_discoverable_skill_outside_catalog_is_rejected(self) -> None:
        directory = self.root / "examples" / "sample-task"
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_text(skill_text(), encoding="utf-8")
        self.assertIn("under skills/", self.errors())

    def test_case_sensitive_filename(self) -> None:
        directory = self.root / "skills" / "sample-task"
        directory.mkdir()
        (directory / "skill.md").write_text(skill_text(), encoding="utf-8")
        self.assertIn("case-sensitive", self.errors())

    def test_loose_catalog_files_are_rejected(self) -> None:
        (self.root / "skills" / "stray.txt").write_text("stray", encoding="utf-8")
        self.assertIn("only README.md", self.errors())

    def test_symlinked_resources_are_rejected(self) -> None:
        directory = self.add_skill()
        target = self.root / "external.txt"
        target.write_text("external", encoding="utf-8")
        (directory / "linked.txt").symlink_to(target)
        self.assertIn("symlinks are not allowed", self.errors())

    def test_python_metadata_is_checked_without_execution(self) -> None:
        self.add_script(
            "# /// script\n"
            '# requires-python = ">=3.11"\n'
            '# dependencies = ["synthetic-package>=1"]\n'
            "# ///\n"
            'raise RuntimeError("Validation must not execute this script")\n'
        )
        self.assertEqual(check_repository(self.root), ([], 1))

    def test_stdlib_python_helpers_accept_empty_dependencies(self) -> None:
        self.add_script(
            '# /// script\n# requires-python = ">=3.11"\n# dependencies = []\n# ///'
        )
        self.assertEqual(check_repository(self.root), ([], 1))

    def test_python_metadata_allows_shebang_crlf_and_tool_settings(self) -> None:
        self.add_script(
            "#!/usr/bin/env -S uv run --script\r\n"
            "# /// script\r\n"
            '# requires-python = ">=3.11"\r\n'
            "#\r\n"
            "# dependencies = []\r\n"
            "# [tool.uv]\r\n"
            "# offline = true\r\n"
            "# ///\r\n"
        )
        self.assertEqual(check_repository(self.root), ([], 1))

    def test_python_helpers_require_one_well_formed_metadata_block(self) -> None:
        block = (
            '# /// script\n# requires-python = ">=3.11"\n# dependencies = []\n# ///\n'
        )
        for content in (
            "pass\n",
            block.removesuffix("# ///\n"),
            block + block,
            block + "# /// script\n",
            block.replace("# dependencies", "dependencies"),
        ):
            with self.subTest(content=content):
                self.add_script(content)
                self.assertIn("well-formed PEP 723", self.errors())
                self.assertIn("scripts/helper.py", self.errors())

    def test_python_metadata_ignores_other_block_types(self) -> None:
        block = (
            '# /// script\n# requires-python = ">=3.11"\n# dependencies = []\n# ///\n'
        )
        other = "# /// custom\n# Not TOML: ignored metadata\n# ///\n"
        for content in (other + block, block + other):
            with self.subTest(content=content):
                self.add_script(content)
                self.assertEqual(check_repository(self.root), ([], 1))

    def test_python_metadata_rejects_invalid_toml(self) -> None:
        self.add_script("# /// script\n# dependencies = [\n# ///\n")
        self.assertIn("Invalid PEP 723 TOML", self.errors())

    def test_python_metadata_requires_explicit_field_types(self) -> None:
        cases = (
            ("# dependencies = []\n", "requires-python"),
            ("# requires-python = 311\n# dependencies = []\n", "requires-python"),
            ('# requires-python = " "\n# dependencies = []\n', "requires-python"),
            ('# requires-python = ">=3.11"\n', "dependencies"),
            ('# requires-python = ">=3.11"\n# dependencies = "rich"\n', "dependencies"),
            ('# requires-python = ">=3.11"\n# dependencies = [42]\n', "dependencies"),
            ('# requires-python = ">=3.11"\n# dependencies = [" "]\n', "dependencies"),
        )
        for fields, expected in cases:
            with self.subTest(fields=fields):
                self.add_script(f"# /// script\n{fields}# ///\n")
                self.assertIn(expected, self.errors())

    def test_nested_python_helpers_are_checked(self) -> None:
        self.add_script("pass\n", "nested/helper.py")
        self.assertIn("scripts/nested/helper.py", self.errors())

    def test_python_helpers_reject_invalid_encoding(self) -> None:
        self.add_script("").write_bytes(b"\xff")
        self.assertIn("Cannot read Python script", self.errors())

    def test_python_metadata_rule_does_not_apply_to_other_scripts(self) -> None:
        self.add_script("exit 0\n", "helper.sh")
        maintenance = self.root / "scripts"
        maintenance.mkdir()
        (maintenance / "validate.py").write_text("pass\n", encoding="utf-8")
        self.assertEqual(check_repository(self.root), ([], 1))

    def test_template_matches_policy_without_publishing_a_skill(self) -> None:
        template = (REPOSITORY / "docs" / "skill-template.md").read_text(
            encoding="utf-8"
        )
        content = template.split("````markdown\n", 1)[1].split("\n````", 1)[0]
        self.add_skill(content.replace("example-task", "sample-task"))
        self.assertEqual(check_repository(self.root), ([], 1))


class DocumentationTests(unittest.TestCase):
    def test_local_markdown_links_resolve(self) -> None:
        documents = [
            *REPOSITORY.glob("*.md"),
            *REPOSITORY.glob("docs/*.md"),
            *REPOSITORY.glob("skills/*.md"),
            REPOSITORY / ".github" / "pull_request_template.md",
        ]
        for document in documents:
            content = document.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc:
                    continue
                with self.subTest(document=document.name, target=target):
                    destination = (document.parent / unquote(parsed.path)).resolve()
                    self.assertTrue(destination.is_relative_to(REPOSITORY))
                    self.assertTrue(destination.exists(), target)
                    if parsed.fragment:
                        headings = re.findall(
                            r"^#{1,6} (.+)$",
                            destination.read_text(encoding="utf-8"),
                            re.MULTILINE,
                        )
                        anchors = {
                            re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-")
                            for heading in headings
                        }
                        self.assertIn(parsed.fragment, anchors)


if __name__ == "__main__":
    unittest.main()
