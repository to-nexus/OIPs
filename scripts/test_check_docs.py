"""Exercise document checks with isolated repositories and deliberately broken inputs."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from check_docs import validate


class DocumentValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / "OIPs").mkdir()
        (self.root / "ORCs").mkdir()
        (self.root / ".gitignore").write_text(".venv/\n", encoding="utf-8")
        (self.root / "README.md").write_text(
            "# Proposals\n\n| Number | Title | Type | Category | Status |\n| --- | --- | --- | --- | --- |\n",
            encoding="utf-8",
        )
        (self.root / "ORCs/README.md").write_text(
            "# Proposals\n\n| Number | Title | Type | Status |\n| --- | --- | --- | --- |\n",
            encoding="utf-8",
        )
        self._proposal("oip", 1)
        self._proposal("orc", 2)

    def _proposal(self, prefix, number, requires=None):
        folder = "OIPs" if prefix == "oip" else "ORCs"
        category = "category: Core\n" if prefix == "oip" else ""
        dependencies = f"requires: {requires}\n" if requires else ""
        text = (
            f"---\n{prefix}: {number}\ntitle: Example\ndescription: An example.\nauthor: Contributors\n"
            f"status: Draft\ntype: Standards Track\n{category}created: 2026-11-13\n{dependencies}---\n\n"
            f"# {prefix.upper()}-{number}: Example\n\n"
        )
        for section in ("Abstract", "Motivation", "Specification", "Rationale", "Backwards Compatibility",
                        "Security Considerations", "Copyright"):
            text += f"## {section}\n\nExample content.\n\n"
        (self.root / folder / f"{prefix}-{number}.md").write_text(text, encoding="utf-8")
        index = self.root / ("README.md" if prefix == "oip" else "ORCs/README.md")
        target = f"OIPs/oip-{number}.md" if prefix == "oip" else f"orc-{number}.md"
        category_cell = " Core |" if prefix == "oip" else ""
        with index.open("a", encoding="utf-8") as stream:
            stream.write(f"| [{prefix.upper()}-{number}]({target}) | Example | Standards Track |{category_cell} Draft |\n")

    def _replace(self, filename, old, new):
        path = self.root / filename
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def test_valid_repository_and_markdown_syntax(self):
        (self.root / "Guide (v1).md").write_text(
            "# Guide\n\n## Run `call()`\n\n## Again\n\n## Again\n", encoding="utf-8",
        )
        (self.root / "links.md").write_text(
            "[guide](<Guide (v1).md#run-call>)\n\n[again][]\n\n"
            "[again]: <Guide (v1).md#again-1>\n\n"
            "```md\n[example](missing.md)\n```\n\n`[example](missing.md)`\n"
            "`[example][missing]`\n\n\\[example][missing]\n\n"
            "<!-- [example](missing.md) -->\n\n[external](https://example.invalid/private)\n",
            encoding="utf-8",
        )
        (self.root / ".venv").mkdir()
        (self.root / ".venv/ignored.md").write_text("[bad](missing.md)", encoding="utf-8")
        self.assertEqual(validate(self.root), [])

    def test_broken_links_and_anchors(self):
        for link, diagnostic in (
            ("[file](missing.md)", "missing link target"),
            ("[anchor](OIPs/oip-1.md#missing)", "missing heading anchor"),
            ("![image](missing.svg)", "missing link target"),
            ("[unused]: missing.md", "missing link target"),
            ("[example][missing]", "undefined link reference"),
            ("[missing][]", "undefined link reference"),
            ("[outside](../outside.md)", "escapes the repository"),
        ):
            with self.subTest(link=link):
                (self.root / "links.md").write_text(link, encoding="utf-8")
                self.assertIn(diagnostic, "\n".join(validate(self.root)))

    def test_ignored_link_target_is_not_publishable(self):
        (self.root / ".venv").mkdir()
        (self.root / ".venv/local.md").write_text("# Local", encoding="utf-8")
        (self.root / "links.md").write_text("[local](.venv/local.md)", encoding="utf-8")
        self.assertIn("not a repository file", "\n".join(validate(self.root)))

    def test_metadata_and_sections(self):
        path = self.root / "OIPs/oip-1.md"
        original = path.read_text(encoding="utf-8")
        for old, new, diagnostic in (
            ("status: Draft", "status: Unknown", "invalid status"),
            ("status: Draft", "status: Draft\nstatus: Review", "duplicate metadata"),
            ("status: Draft", "status: Last Call", "last-call-deadline"),
            ("status: Draft", "status: Withdrawn", "withdrawal-reason"),
            ("status: Draft", "status: Living", "Living is limited"),
            ("created: 2026-11-13", "created: 2026-02-30", "valid YYYY-MM-DD"),
            ("category: Core\n", "", "require a valid category"),
            ("author: Contributors\n", "", "missing required metadata field: author"),
            ("oip: 1", "oip: 3", "filename and metadata number differ"),
            ("# OIP-1: Example", "# OIP-1: Wrong", "expected one top-level heading"),
            ("## Security Considerations", "## Other", "missing required section"),
            ("## Motivation", "## Abstract", "duplicated or out of"),
            ("description: An example.", "description: [An example.]", "must be scalar"),
        ):
            with self.subTest(new=new):
                path.write_text(original.replace(old, new, 1), encoding="utf-8")
                self.assertIn(diagnostic, "\n".join(validate(self.root)))
        path.write_text(original.replace("title: Example", 'title: "Example"'), encoding="utf-8")
        self.assertEqual(validate(self.root), [])

    def test_unnumbered_submission_fails_merge_check(self):
        path = self.root / "OIPs/oip-1.md"
        path.rename(self.root / "OIPs/oip-draft-example.md")
        self.assertIn("assign a number before merge", "\n".join(validate(self.root)))

    def test_shared_number_collision(self):
        self._proposal("orc", 1)
        self.assertIn("number 1 is already assigned", "\n".join(validate(self.root)))

    def test_dependency_namespace_and_cycle(self):
        self._proposal("oip", 3, "2")
        self.assertIn("missing dependency in the same namespace: OIP-2", "\n".join(validate(self.root)))
        self._replace("OIPs/oip-3.md", "requires: 2", "requires: 1")
        self._replace("OIPs/oip-1.md", "created: 2026-11-13", "created: 2026-11-13\nrequires: 3")
        self.assertIn("dependency cycle", "\n".join(validate(self.root)))

    def test_final_dependency_status(self):
        self._proposal("oip", 3, "1")
        self._replace("OIPs/oip-3.md", "status: Draft", "status: Final")
        self.assertIn("OIP-1 must be Final or Living", "\n".join(validate(self.root)))

    def test_index_matches_metadata_and_has_no_duplicates(self):
        self._replace("README.md", "| Core | Draft |", "| Interface | Final |")
        self.assertIn("outdated index row", "\n".join(validate(self.root)))
        index = self.root / "ORCs/README.md"
        with index.open("a", encoding="utf-8") as stream:
            stream.write(index.read_text(encoding="utf-8").splitlines()[-1] + "\n")
        self.assertIn("duplicate index row", "\n".join(validate(self.root)))

    def test_index_examples_in_code_are_ignored(self):
        index = self.root / "README.md"
        with index.open("a", encoding="utf-8") as stream:
            stream.write("\n```md\n| [OIP-99](OIPs/oip-99.md) | Example | Meta | — | Draft |\n```\n")
        self.assertEqual(validate(self.root), [])

    def test_internal_source_notice(self):
        path = self.root / "evidence.md"
        source = "[source](https://github.com/to-nexus/stake-one-contracts/blob/revision/example.sol)\n"
        path.write_text(source, encoding="utf-8")
        self.assertIn("mark to-nexus/stake-one-contracts", "\n".join(validate(self.root)))
        path.write_text(source + "[internal verification sources](README.md)\n", encoding="utf-8")
        self.assertEqual(validate(self.root), [])

    def test_cli_exit_status_and_diagnostic(self):
        scripts = self.root / "scripts"
        scripts.mkdir()
        script = scripts / "check_docs.py"
        shutil.copyfile(Path(__file__).with_name("check_docs.py"), script)
        command = [sys.executable, "-B", str(script)]
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        (self.root / "broken.md").write_text("[bad](missing.md)", encoding="utf-8")
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("broken.md:1: missing link target", result.stderr)


if __name__ == "__main__":
    unittest.main()
