"""Public-edition manifest CLI regression tests using disposable inventories."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ManifestTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "scripts").mkdir()
        self.script = self.root / "scripts" / "verify_manifest.py"
        shutil.copyfile(Path(__file__).resolve().parents[1] / "scripts" / "verify_manifest.py", self.script)
        self.target = self.root / "payload.bin"
        self.set_payload("café\n".encode("utf-8"))

    def set_payload(self, payload):
        self.target.write_bytes(payload)
        self.manifest = {"edition_files": [
            {"path": path.relative_to(self.root).as_posix(),
             "size": len(path.read_bytes()),
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in (self.script, self.target)
        ]}
        self.entry = self.manifest["edition_files"][1]

    def check(self, valid, error=None):
        (self.root / "PROVENANCE.json").write_text(json.dumps(self.manifest), encoding="utf-8")
        result = subprocess.run([sys.executable, str(self.script)], cwd=self.root,
                                capture_output=True, text=True, timeout=10)
        if valid:
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["valid"])
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
            if error:
                self.assertIn(error, result.stderr)

    def test_valid_empty_ascii_and_multibyte_sizes(self):
        for payload in (b"", b"x", b"normal bytes\n", "café\n".encode("utf-8")):
            with self.subTest(payload=payload):
                self.set_payload(payload)
                self.check(True)

    def test_size_only_drift_is_rejected_with_correct_hash(self):
        for delta in (-1, 1):
            with self.subTest(delta=delta):
                self.set_payload(b"abc")
                self.entry["size"] += delta
                self.check(False, "size mismatch")

    def test_missing_size_is_rejected(self):
        del self.entry["size"]
        self.check(False, "invalid declared size")

    def test_invalid_size_types_and_negative_value_are_rejected(self):
        for size in (None, "6", [], {}, -1, 6.0, 1.5, True, False):
            with self.subTest(size=size):
                self.entry["size"] = size
                self.check(False, "invalid declared size")

    def test_numeric_equality_does_not_accept_bool_or_float(self):
        for payload, size in ((b"x", True), (b"", False), (b"x", 1.0), (b"", 0.0)):
            with self.subTest(payload=payload, size=size):
                self.set_payload(payload)
                self.entry["size"] = size
                self.check(False, "invalid declared size")

    def test_character_count_is_not_byte_count(self):
        self.entry["size"] = len(self.target.read_text(encoding="utf-8"))
        self.check(False, "size mismatch")

    def test_same_size_tampering_still_fails_checksum(self):
        self.set_payload(b"abc")
        self.target.write_bytes(b"xyz")
        self.check(False, "checksum mismatch")

    def test_refreshed_hash_does_not_excuse_stale_size(self):
        self.target.write_bytes(b"longer replacement bytes")
        self.entry["sha256"] = hashlib.sha256(self.target.read_bytes()).hexdigest()
        self.check(False, "size mismatch")

    def test_consistent_replacement_bytes_hash_and_size_pass(self):
        self.set_payload(b"replacement bytes")
        self.check(True)

    def test_duplicate_path_still_rejected(self):
        self.manifest["edition_files"].append(dict(self.entry))
        self.check(False, "duplicate manifest path")

    def test_missing_extra_and_nested_manifest_still_rejected(self):
        self.target.unlink()
        self.check(False, "inventory mismatch")
        self.target.write_bytes(b"restored")
        self.set_payload(b"restored")
        extra = self.root / "extra.txt"
        extra.write_bytes(b"extra")
        self.check(False, "inventory mismatch")
        extra.unlink()
        (self.root / "scripts" / "PROVENANCE.json").write_text("{}")
        self.check(False, "inventory mismatch")

    def test_symlink_still_rejected(self):
        self.target.unlink()
        self.target.symlink_to(self.script)
        self.entry["size"] = len(self.script.read_bytes())
        self.entry["sha256"] = hashlib.sha256(self.script.read_bytes()).hexdigest()
        self.check(False, "symlink or escaped path")


if __name__ == "__main__":
    unittest.main()
