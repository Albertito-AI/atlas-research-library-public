# Curation and preservation methods

## Purpose and scope

A research library should let a reader identify what a resource is, where it came from, which version was used, what may be done with it, and how far it has been checked. These questions remain separate throughout this workflow. A correctly computed checksum can establish that two byte sequences match. It cannot establish that a theorem is true, a document is authentic or a copy is permitted.

This guide adapts the Atlas Research Library's original formats, provenance and operator guidance into a public methods edition. It describes a practical workflow implemented by the included catalogue validator. It is not an evaluation study of library effectiveness. The private collection, its full catalogue and its access administration are outside this publication.

## 1. Define the research object

Begin with the question, assumptions, method, result and unresolved limitations. Retain useful unsuccessful attempts when they explain why a method failed or what a subsequent attempt should change. Identify whether the object is a source document, working explanation, dataset, computational check, formal proof, teaching exercise or review.

A research object may have several formats. An editable document and a fixed-layout rendering can be related without being identical. A notebook and its exported results require different evidence. A video may explain a result while omitting the steps needed to reproduce it. Describe these relationships rather than treating every format as interchangeable.

Choose a stable catalogue identifier and a title that identifies the actual object. A suitable identifier is lowercase, begins with a letter, and contains letters, digits, hyphens or underscores. It should remain stable across corrections to descriptive metadata. A materially different source version should remain separately traceable.

## 2. Decide whether to copy or reference

For each candidate resource, check its source, rights, audience and research value. An external link is often sufficient when a source is already public or copying permission is unresolved. A catalogue reference identifies a location; it does not guarantee that the location will remain available or that every reader has access.

For a permitted local copy, record the exact source version and keep required licence and attribution notices with the copy. A repository snapshot should use an immutable complete commit identifier. Branch names and a label such as “latest” do not identify fixed bytes. The included schema accepts a 40-character lowercase Git commit identifier in `source_commit`.

Private correspondence, access administration, confidential manuscripts, reviewer reports and assessment records do not become publishable because they are adjacent to research material. They require separate treatment and are excluded from this public edition. Avoid blanket repository exports when a selected package can identify the intended research object more precisely.

## 3. Record rights per resource

Each record includes a human-readable `licence` statement. The optional `rights_basis` field records one of four bases:

| Basis | Interpretation |
| --- | --- |
| `open-licence` | A specific source licence is identified; preserve its scope and notices. |
| `owned-original` | The resource is an original work controlled by the relevant rights holder. Public distribution and further reuse still require their respective permissions. |
| `permission-recorded` | A permission basis has been documented separately; confidential agreements do not belong in the public catalogue. |
| `link-only` | Only an external reference is included. It cannot accompany a local copy in this validator. |

The validator records and checks these labels; it cannot make legal determinations. A source's public visibility does not, by itself, grant redistribution rights. Public-source material retains its upstream terms, and private curation does not make an existing open licence exclusive.

The historical schema has `access` values `public-source` and `members`. In this publication, `public-source` records the public origin of an external reference. The `members` value remains in the inherited schema and synthetic tests for compatibility; it is not an enrolment system, a subscription, a permission grant or a claim that this publication is restricted to members. The example uses it only as a legacy classification for an owner-original resource.

## 4. Describe location and integrity

For a local file, set `path` to its relative POSIX path, `external_url` to null, and `sha256` to the hash measured from the actual bytes. The validator rejects absolute paths, traversal, hidden path components, symlinks and files outside the selected root. It checks that the suffix is compatible with the stated format.

For an external reference, set `path` to null and provide an HTTPS `external_url` without embedded credentials. A checksum may be null when bytes have not been acquired. Such a resource remains a reference or working draft. A stored checksum for an external resource documents a prior acquisition; this offline validator does not download the current remote object or establish that it still matches.

| Format group | Information worth retaining |
| --- | --- |
| Markdown, text and HTML | Source, citations and revision. |
| Word and PDF | Relation between editable and rendered versions; whether content is equivalent. |
| CSV, JSON, JSONL and spreadsheets | Field definitions, units, data provenance and calculation assumptions. |
| Lean and other formal artefacts | Toolchain, dependencies, exact statement and actual verification evidence. |
| Notebooks and Python | Environment, inputs, execution instructions and generated outputs. |
| Audio, video and images | Source, media rights and captions or transcripts where available. |
| ZIP archives | File manifest, source revision, applicable notices and inspection scope. |

Small permitted files can be retained directly. Large resources may remain in an appropriate external repository with a stable reference and explicit access requirements. File size or format alone does not determine the quality or sufficiency of preservation.

## 5. State the scope of checking

Use the status vocabulary consistently:

| Status | What it records |
| --- | --- |
| `reference` | A resource has been identified. Its contents have not been verified by this workflow. |
| `working-draft` | The material is provisional. |
| `integrity-checked` | The relevant bytes have been checked against the recorded checksum. |
| `reviewed` | A substantive review is recorded in `verification_note`, including its scope. |

A review note should say what was examined, by which method, with what result and what remains outside the review. For example, checking that a lesson follows its cited calculations does not establish the novelty of those calculations. Compiling a formal file establishes only what the named formal environment checked. Passing demonstration tests does not establish a general claim about learning or real-world performance.

The validator requires a review note for `reviewed` records and requires a recorded checksum for checked or reviewed external records. These requirements make unsupported labels harder to add accidentally. A malicious or mistaken operator could still enter an inaccurate note or hash. The system therefore supports accountable documentation rather than replacing human judgement.

## 6. Validate before packaging

Run the catalogue validator from the package root. It checks the permitted fields, identifier uniqueness, location uniqueness, allowed formats, source identifiers, URL shape and local byte hashes. It makes no network calls. The separate manifest check verifies the edition's recorded file hashes and rejects unexpected non-generated files.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_library.py
python3 scripts/validate_library.py --catalogue examples/catalogue.json
python3 scripts/verify_manifest.py
```

The regression tests include hostile path inputs, changed local bytes, credential-bearing URLs, missing provenance, duplicate records and attempts to mark a source reviewed without a note. These are checks of specific implementation behaviour. They are not an exhaustive security audit.

The schema is supplied as documentation of the catalogue contract. The Python validator implements the operational checks without requiring a JSON Schema library. There may be differences between a generic schema validator and the Python implementation; this release reports the results of the included Python checks.

## 7. Preserve corrections and cite precisely

Retain an immutable release package, a manifest of actual bytes and the source revision used to prepare it. Record the date and scope of substantive corrections. If a source changes, identify dependent explanations and revisit them. Avoid replacing evidence silently under an unchanged reference.

For citation, identify the version actually used. A persistent identifier can make the release easier to find and cite; the metadata must still describe the work accurately. A methods edition, its code and any separate research outputs should be linked without presenting the same intellectual contribution as several independent discoveries.

This edition includes three public references to illustrate link-only records. The external works retain their own citation identities. No result from those projects is claimed as a new result of this edition.

## Adaptation record

This guide is adapted from the owner's `README.md`, `docs/FORMATS_AND_PRESERVATION.md`, `docs/RIGHTS_AND_PROVENANCE.md` and `docs/OPERATOR_CHECKLIST.md` at source commit `123f1a90cbc61b4b994acddec2689c1256d93755`. Administrative instructions have been omitted. Edition-specific explanations of the legacy access field, offline checks, example and release manifest have been added. `PROVENANCE.json` records the source identifiers; the private repository is not required to run this edition.
