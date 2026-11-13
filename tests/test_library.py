"""Catalogue integrity and trust-boundary regression tests."""
import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "validate_library", Path(__file__).resolve().parents[1] / "scripts" / "validate_library.py"
)
library = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(library)


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "docs").mkdir()
        (self.root / "docs" / "guide.md").write_text("A reproducible reading guide.\n")
        self.entry = {
            "id": "reading-guide", "title": "Reading guide", "format": "md",
            "path": "docs/guide.md", "external_url": None,
            "sha256": library.sha256(self.root / "docs" / "guide.md"),
            "source_url": None, "source_commit": None,
            "licence": "Original guide, reserved rights", "access": "members",
            "status": "integrity-checked", "description": "A teaching guide.",
            "rights_basis": "owned-original",
        }

    def check(self, entry=None):
        return library.validate({"schema_version": 1, "entries": [entry or self.entry]}, self.root)

    def test_valid_local_bytes_and_count(self):
        result = self.check()
        self.assertTrue(result["valid"])
        self.assertEqual(result["local_files"], 1)

    def test_changed_bytes_are_rejected(self):
        (self.root / "docs" / "guide.md").write_text("Changed after review.\n")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.check()

    def test_missing_file_is_rejected(self):
        (self.root / "docs" / "guide.md").unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            self.check()

    def test_path_traversal_and_hidden_files_are_rejected(self):
        for path in ("../outside.md", "/tmp/outside.md", ".git/config", "docs/../guide.md", "docs\\guide.md"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.check(dict(self.entry, path=path))

    def test_symlinked_parent_is_rejected(self):
        (self.root / "linked").symlink_to(self.root / "docs", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlinks"):
            self.check(dict(self.entry, path="linked/guide.md"))

    def test_external_reference_can_remain_unverified(self):
        entry = dict(self.entry, path=None, external_url="https://example.org/resource.pdf",
                     sha256=None, format="pdf", status="reference", rights_basis="link-only")
        self.assertEqual(self.check(entry)["external_references"], 1)

    def test_external_urls_reject_credentials_and_unsafe_schemes(self):
        for url in ("https://name:secret@example.org/file.pdf", "http://example.org/file.pdf",
                    "javascript:alert(1)", "https://example.org/\nfile.pdf", "https://example.org\\@evil.test"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.check(dict(self.entry, path=None, external_url=url, sha256=None, status="reference"))

    def test_external_checked_status_needs_checksum(self):
        with self.assertRaisesRegex(ValueError, "checksum"):
            self.check(dict(self.entry, path=None, external_url="https://example.org/file.md", sha256=None))

    def test_duplicate_identifiers_and_locations_are_rejected(self):
        for second in (copy.deepcopy(self.entry), dict(self.entry, id="another-id")):
            with self.subTest(second=second["id"]), self.assertRaisesRegex(ValueError, "duplicate"):
                library.validate({"schema_version": 1, "entries": [self.entry, second]}, self.root)

    def test_unknown_fields_rejected(self):
        with self.assertRaisesRegex(ValueError, "fields"):
            self.check(dict(self.entry, member_email="do-not-store@example.org"))

    def test_format_must_match_local_extension(self):
        with self.assertRaisesRegex(ValueError, "format"):
            self.check(dict(self.entry, format="pdf"))

    def test_review_requires_explanation_of_scope(self):
        with self.assertRaisesRegex(ValueError, "verification_note"):
            self.check(dict(self.entry, status="reviewed"))
        self.assertTrue(self.check(dict(self.entry, status="reviewed", verification_note="Reviewed for exposition only."))["valid"])

    def test_source_commit_must_be_full_and_attributed(self):
        for commit in ("abcdef", "g" * 40, "a" * 40):
            with self.subTest(commit=commit), self.assertRaises(ValueError):
                self.check(dict(self.entry, source_commit=commit))
        self.assertTrue(self.check(dict(self.entry, source_commit="a" * 40,
                                       source_url="https://github.com/example/project/blob/" + "a" * 40 + "/guide.md"))["valid"])

    def test_link_only_does_not_authorise_copy(self):
        with self.assertRaisesRegex(ValueError, "link-only"):
            self.check(dict(self.entry, rights_basis="link-only"))

    def test_boolean_schema_version_rejected(self):
        with self.assertRaisesRegex(ValueError, "schema_version"):
            library.validate({"schema_version": True, "entries": []}, self.root)

    def test_all_requested_formats_supported(self):
        for format_name in ("docx", "pdf", "csv", "json", "jsonl", "lean", "ipynb", "video"):
            with self.subTest(format=format_name):
                self.assertIn(format_name, library.FORMATS)


if __name__ == "__main__":
    unittest.main()
