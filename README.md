# NOVA Q / EIT — CBi relativistic bonding V0.3.0

**Research code and independently audited secondary computational reanalysis.** This release does not introduce new quantum-chemical simulations, independent experimental spectra, or a new confirmed physical law. The original relativistic bonding discovery is by Kahraman *et al.*, *Science* 393, 184–187 (2026), DOI: https://doi.org/10.1126/science.aei1285.

## Scientific scope and evidence
- Selected existing Dirac–Fock reference-spinor Mulliken populations from 6 DIRAC `.out` files (CBi− anion and neutral CBi X/A, each in 3z/4z bases).
- 18/18 selected spinor entries and 18/18 printed AO-label/symmetry structures checked; 108/108 compared local fields agreed in the conducted cross-audit.
- `M_pop=4 p_alpha p_beta` is a **conditional** operational population proxy for the inspected |m_j|=1/2 blocks with observed axial/transverse AO labels. It is not a universal spin–orbit mixing measure, bond order, experimental observable, or coupled-cluster state decomposition.
- Printed AO columns are thresholded; maximum displayed-sum versus Gross Total difference = 0.0345. Gross Total is authoritative for this proxy.
- P1/P2/P4 and controlled SOC-lambda sweep are unresolved; P3 basis robustness is partial. External review and physical modeling remain desirable.

## Public self-test (no third-party private inputs)
```sh
python3 scripts/verify_public_release.py
python3 scripts/verify_derived_agreement.py
```
These check *derived numerical consistency*, not independent authenticity of source archives or scientific correctness. Read `audit/` for local provenance and disclaimers.

## Full local extraction with legitimately obtained source inputs
The original three DIRAC ZIP files are **not included**. If separately and lawfully obtained, check hashes in `audit/private_input_fingerprints.json` and use:
```sh
python3 scripts/audit_spinors_v02.py --data-dir /path/to/private-inputs --out-dir /tmp/cbi-run
python3 scripts/cbi_ao_reconstruction_v02.py --data-dir /path/to/private-inputs --manifest audit/private_input_fingerprints.json --output-dir /tmp/cbi-ao
```
These scripts post-process output. They do not run quantum chemistry software.

## License and authorship
Copyright (c) 2026 Toni Mladenovski for original author-created contributions. Code: **PolyForm Noncommercial License 1.0.0**; original documentation, derived datasets and figures: **CC BY-NC-SA 4.0**. See `LICENSE` and `LICENSES.md`. These terms do **not** license the original third-party DIRAC archives or published Science material. AI systems assisted with implementation, audit, and manuscript production; scientific conclusions remain limited by the evidence.

## Publication pairing
The manuscript is a distinct *preprint* record and should obtain a separate Zenodo DOI; this software gets a DOI only after a public release is archived. Insert actual assigned DOI(s) in `CITATION.cff` and related identifiers once published. **Neither DOI is preassigned by this ZIP.**
