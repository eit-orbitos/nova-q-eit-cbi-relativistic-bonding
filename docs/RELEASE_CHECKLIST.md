# Final publication sequence — CBi V0.3.0

1. Re-run `python3 scripts/verify_public_release.py` and `python3 scripts/verify_derived_agreement.py` before release.
2. Review original input-derived CSV data rights / provenance. The original third-party DIRAC archives are not redistributable from this package.
3. Create a dedicated GitHub repository `nova-q-eit-cbi-relativistic-bonding`; unpack this software archive into repository root.
4. Connect that repository in Zenodo GitHub integration **before** tagging a new release.
5. Tag `v0.3.0` and publish a GitHub Release; verify Zenodo ingests it as a separate Software record. Select a license entry matching the actual software license or use an accurate 'Other' license with a link; do not silently assign MIT/Apache/CC BY to code.
6. Separately deposit the single preprint PDF in Zenodo as Publication > Preprint with **CC BY-NC-SA 4.0**; note author, version, original DOI and no peer review.
7. When both DOIs exist, insert related identifiers and update `CITATION.cff` in a later *new* release/version if desired. Do not alter immutable published archive bytes.

No published DOI or platform event is claimed by this local preparation.
