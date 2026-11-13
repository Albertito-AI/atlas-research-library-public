# Atlas Research Library: Curation and Preservation Methods

Version 1.0.0 · 13 November 2026

Albert Tan Sin Hon · ORCID [0009-0001-8996-7933](https://orcid.org/0009-0001-8996-7933)

Public edition repository: [atlas-research-library-public](https://github.com/Albertito-AI/atlas-research-library-public).

This public methods edition explains how the Atlas Research Library describes, checks and preserves research resources. It contains a practical guide, a catalogue schema, the existing offline validator and its regression tests, three link-only public references, and a fictional worked example. It is a selected publication package from the owner-managed research library. The source repository and its research collection remain private.

The contribution of this edition is a documented curation workflow with executable checks for metadata and byte integrity. It reports no new mathematical result and makes no claim of independent peer review, demonstrated learning effectiveness or automated legal clearance.

## Read and reproduce

1. Read [Curation and preservation methods](docs/METHODS.md).
2. Follow the [worked example](examples/README.md) to distinguish a source reference, a local byte check and a substantive review.
3. Inspect the [public reference catalogue](data/catalogue.json) and [catalogue schema](schemas/catalogue.schema.json).
4. Run the checks below with Python 3.10 or later. Only the Python standard library is required. The checks make no network calls.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_library.py
python3 scripts/validate_library.py --catalogue examples/catalogue.json
python3 scripts/verify_manifest.py
```

The default catalogue holds three external public source references. `reference` means the validator has not acquired or verified their remote contents. The fictional local example is checked against its measured checksum. The test suite exercises changed bytes, unsafe paths, symlinks, duplicate records, credential-bearing URLs, missing provenance and overstated verification labels.

## Publication scope

The edition adapts the original library's formats, provenance and curation guidance for public use. Existing validation code and tests retain their MIT licence. The schema and three reference records are selected from the source repository. The provenance manifest identifies the exact source revision and the derivation of included files.

Excluded material includes the private catalogue, mirrored research collections, access administration, membership drafts, private School records and confidential editorial material. No Git history is included. The linked public projects remain separate works under their own rights; their research results are not republished here as new findings.

Read [RIGHTS.md](RIGHTS.md) before reuse. Original prose and catalogue material retain reserved rights. Public readability does not create a blanket open-content licence. The code licence applies only within its stated scope.

## Citation and limitations

Use [CITATION.cff](CITATION.cff) for the title, author and version. The exact citation identifier can be added after deposit publication; no DOI is asserted in this source package.

Validation establishes conformity with the implemented checks. It does not prove the truth of a research claim, authenticate an author, assess scholarly quality, confirm a reader's access, or determine whether copying is legally permitted. [VALIDATION.md](VALIDATION.md) records the checks performed for this edition. Preservation here means retaining identifiable files and their provenance; long-term institutional preservation depends on the repository where the release is deposited.
