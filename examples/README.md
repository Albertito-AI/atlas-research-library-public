# Worked example: identity, integrity and review

This example is fictional and was created for this public edition. It uses a short arithmetic note in [sample-note.md](sample-note.md). The note contains no private research result or person-specific information.

The corresponding [catalogue](catalogue.json) records a local resource, reserved rights and a measured SHA-256 value. It is marked `integrity-checked` because its bytes are checked. The catalogue does not claim a substantive external review. The legacy `members` access label describes an owner-original resource classification; this example is publicly readable and creates no membership or access entitlement.

Run from the repository root:

```sh
python3 scripts/validate_library.py --catalogue examples/catalogue.json
```

Expected result: one local file, zero external references and `valid: true`.

To see the boundary, copy the package to a temporary directory, alter the arithmetic note and run the same command there. The validator reports a SHA-256 mismatch. It detects the changed bytes regardless of whether the edit improved or worsened the arithmetic. After an intentional revision, review it and recompute its hash as part of creating the next version. Do not erase the earlier evidence merely to obtain a passing result.

The automated tests exercise this failure without modifying the release package. They also demonstrate that a `reviewed` label requires a note, but cannot prove the note is truthful. Read `docs/METHODS.md` for the meaning and limits of each status.
