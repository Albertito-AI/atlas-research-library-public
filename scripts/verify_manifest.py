#!/usr/bin/env python3
"""Check the public edition's file inventory, sizes and SHA-256 values, without network access.

Copyright (c) 2026 Albert Tan Sin Hon. MIT licence: see LICENSE-CODE.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "PROVENANCE.json").read_text(encoding="utf-8"))
    files = manifest["edition_files"]
    expected = {item["path"] for item in files}
    if len(expected) != len(files):
        raise ValueError("duplicate manifest path")
    actual = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file()
        and ".git" not in p.relative_to(root).parts
        and "__pycache__" not in p.relative_to(root).parts
        and p.suffix != ".pyc"
        and p.relative_to(root).as_posix() != "PROVENANCE.json"
    }
    if actual != expected:
        raise ValueError(f"inventory mismatch: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
    for item in files:
        path = PurePosixPath(item["path"])
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("unsafe manifest path")
        target = root / path
        if target.is_symlink() or not target.resolve().is_relative_to(root):
            raise ValueError("symlink or escaped path")
        declared_size = item.get("size")
        if type(declared_size) is not int or declared_size < 0:
            raise ValueError(f"invalid declared size: {path}")
        payload = target.read_bytes()
        if len(payload) != declared_size:
            raise ValueError(f"size mismatch: {path}")
        measured = hashlib.sha256(payload).hexdigest()
        if measured != item["sha256"]:
            raise ValueError(f"checksum mismatch: {path}")
    print(json.dumps({"valid": True, "files": len(files), "scope": "edition inventory and local byte integrity only"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
