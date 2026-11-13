#!/usr/bin/env python3
"""Validate the private library catalogue and local file integrity; no network calls."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit


FORMATS = {
    "md": {".md"}, "txt": {".txt"}, "html": {".html", ".htm"},
    "docx": {".docx"}, "pdf": {".pdf"}, "csv": {".csv"},
    "json": {".json"}, "jsonl": {".jsonl"}, "xlsx": {".xlsx"}, "lean": {".lean"},
    "ipynb": {".ipynb"}, "py": {".py"}, "zip": {".zip"},
    "video": {".mp4", ".webm", ".mov", ".mkv"},
    "audio": {".mp3", ".wav", ".ogg", ".m4a", ".flac"},
    "image": {".png", ".jpg", ".jpeg", ".svg", ".webp"},
}
REQUIRED = {
    "id", "title", "format", "path", "external_url", "sha256",
    "source_url", "source_commit", "licence", "access", "status", "description",
}
OPTIONAL = {"rights_basis", "verification_note"}
STATUSES = {"working-draft", "reference", "integrity-checked", "reviewed"}
ACCESS = {"members", "public-source"}
RIGHTS = {"open-licence", "owned-original", "permission-recorded", "link-only"}


def _https(value: object, label: str) -> None:
    if not isinstance(value, str) or not value or len(value) > 4096:
        raise ValueError(f"{label}: expected an HTTPS URL")
    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError(f"{label}: control characters are not permitted")
    try:
        parts = urlsplit(value)
        _ = parts.port
    except ValueError as exc:
        raise ValueError(f"{label}: malformed URL") from exc
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
        raise ValueError(f"{label}: use HTTPS without embedded credentials")
    if "\\" in value or any(c.isspace() for c in value):
        raise ValueError(f"{label}: URL contains whitespace or backslashes")


def _text(value: object, label: str, maximum: int = 2000) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"{label}: expected non-empty text up to {maximum} characters")
    if any(ord(c) < 32 and c not in "\n\t" for c in value):
        raise ValueError(f"{label}: contains a control character")


def _file(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value or "\\" in value or len(value) > 500:
        raise ValueError("path: expected a safe relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or str(path) != value or any(
        part in {".", ".."} or part.startswith(".") for part in path.parts
    ) or ":" in value:
        raise ValueError("path: traversal, hidden and absolute paths are not permitted")
    target = root
    for part in path.parts:
        target = target / part
        if target.is_symlink():
            raise ValueError("path: symlinks are not permitted")
    resolved = target.resolve()
    if not resolved.is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError("path: local file is missing or outside the library")
    return target


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(data: object, root: Path) -> dict:
    """Raise ValueError on invalid metadata or bytes, returning a concise summary."""
    if not isinstance(data, dict) or set(data) != {"schema_version", "entries"}:
        raise ValueError("catalogue requires exactly schema_version and entries")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("unsupported schema_version")
    entries = data["entries"]
    if not isinstance(entries, list) or len(entries) > 10000:
        raise ValueError("entries must be a list of at most 10000 items")
    identifiers, locations = set(), set()
    counts = {"entries": len(entries), "local_files": 0, "external_references": 0}
    for index, entry in enumerate(entries):
        prefix = f"entry {index}"
        try:
            if not isinstance(entry, dict) or not REQUIRED <= set(entry) or set(entry) - REQUIRED - OPTIONAL:
                raise ValueError("entry fields do not match schema")
            if not isinstance(entry["id"], str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,79}", entry["id"]):
                raise ValueError("id must be a lowercase stable identifier")
            if entry["id"] in identifiers:
                raise ValueError("duplicate id")
            identifiers.add(entry["id"])
            for key in ("title", "licence", "description"):
                _text(entry[key], key)
            for key, options in (("format", FORMATS), ("status", STATUSES), ("access", ACCESS)):
                if not isinstance(entry[key], str) or entry[key] not in options:
                    raise ValueError(f"unsupported {key}")
            if "rights_basis" in entry and entry["rights_basis"] not in RIGHTS:
                raise ValueError("unsupported rights_basis")
            if "verification_note" in entry:
                _text(entry["verification_note"], "verification_note", 4000)
            if entry["status"] == "reviewed" and not entry.get("verification_note"):
                raise ValueError("reviewed status requires a verification_note with scope")
            if entry["source_url"] is not None:
                _https(entry["source_url"], "source_url")
            if entry["source_commit"] is not None and (
                not isinstance(entry["source_commit"], str)
                or not re.fullmatch(r"[a-f0-9]{40}", entry["source_commit"])
            ):
                raise ValueError("source_commit must be a complete lowercase Git SHA or null")
            if entry["source_commit"] is not None and entry["source_url"] is None:
                raise ValueError("source_commit needs source_url")
            if entry["access"] == "public-source" and entry["source_url"] is None:
                raise ValueError("public-source needs source_url")
            if entry["sha256"] is not None and (
                not isinstance(entry["sha256"], str)
                or not re.fullmatch(r"[a-f0-9]{64}", entry["sha256"])
            ):
                raise ValueError("sha256 must be 64 lowercase hexadecimal characters or null")
            if (entry["path"] is None) == (entry["external_url"] is None):
                raise ValueError("provide exactly one of path and external_url")
            if entry["path"] is not None:
                if entry.get("rights_basis") == "link-only":
                    raise ValueError("link-only rights cannot accompany a local copy")
                target = _file(root, entry["path"])
                if target.suffix.lower() not in FORMATS[entry["format"]]:
                    raise ValueError("format does not match the local file extension")
                if entry["sha256"] is None or sha256(target) != entry["sha256"]:
                    raise ValueError("local SHA-256 does not match the actual bytes")
                location = ("path", entry["path"])
                counts["local_files"] += 1
            else:
                _https(entry["external_url"], "external_url")
                if entry["sha256"] is None and entry["status"] in {"integrity-checked", "reviewed"}:
                    raise ValueError("external checked/reviewed records need a recorded checksum")
                location = ("external_url", entry["external_url"])
                counts["external_references"] += 1
            if location in locations:
                raise ValueError("duplicate resource location")
            locations.add(location)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"{prefix}: {exc}") from exc
    return {"valid": True, **counts, "scope": "metadata and local byte integrity only"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--catalogue", type=Path, default=Path("data/catalogue.json"))
    args = parser.parse_args(argv)
    path = args.catalogue if args.catalogue.is_absolute() else args.root / args.catalogue
    try:
        if path.stat().st_size > 10 * 1024 * 1024:
            raise ValueError("catalogue exceeds the 10 MiB metadata limit")
        data = json.loads(path.read_text(encoding="utf-8"))
        result = validate(data, args.root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
