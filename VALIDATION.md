# Validation record

Edition: 1.0.0, 13 November 2026.

| Check | Observed result | Scope |
| --- | --- | --- |
| Original validator regression suite | 16 tests passed | Implemented catalogue and local integrity checks, including negative inputs. |
| Public reference catalogue | Valid: 3 external references, 0 local files | Metadata syntax and permitted field combinations. No remote contents downloaded by the validator. |
| Fictional worked example catalogue | Valid: 1 local file, 0 external references | Metadata plus the included note's actual SHA-256. |
| Five selected unchanged source files | Git blob identifiers matched the actual included bytes | Exact source identity for validator, tests, schema, licence and seed catalogue (renamed to `data/catalogue.json`). |
| Edition manifest | Inventory and SHA-256 check passed | All edition files except the self-referential manifest, Git administration and generated Python caches. |
| Manifest negative checks | Changed content, an unexpected extra file and an unexpected nested `PROVENANCE.json` were rejected in temporary copies | Three deliberately altered copies; the release package was unchanged. Only the root manifest is excluded from its own inventory. |

The Atlas Open Mathematics and Atlas Opsbook repository metadata were checked and both repositories were public at preparation. The journal homepage could not be retrieved by the lookup service used in this preparation. All three entries remain `reference`; their remote contents, availability and scholarly claims are not certified by this edition.

The guide, example and selected records were reviewed for publication scope. The package contains no private collection snapshots, administrative records or source repository history. Examples of unsafe addresses and credentials in the regression tests are synthetic negative-test strings using example domains, not working credentials.

This validation record is an implementation and publication-scope record. It does not establish peer review, mathematical novelty, legal clearance of third-party material or general security assurance. Original content rights and limitations are specified in `RIGHTS.md` and `docs/METHODS.md`.
