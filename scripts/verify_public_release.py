#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Toni Mladenovski (original project contributions)
"""Validate distributed post-processed values without relying on private DIRAC ZIP files.

This checks internal consistency only, not experimental confirmation or provenance.
"""
import csv, json, math
from pathlib import Path
root=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((root/'data'/'spinor_ao_audit_18.csv').open(encoding='utf-8')))
assert len(rows)==18, len(rows)
counts={}
max_delta=0
for r in rows:
    key=(r['state'],r['basis']); counts[key]=counts.get(key,0)+1
    a,b=float(r['alpha_gross']),float(r['beta_gross'])
    assert math.isclose(4*a*b,float(r['M_4_alpha_beta']),abs_tol=1e-10)
    assert math.isclose(a+b,1.0,abs_tol=1e-8)
    max_delta=max(max_delta,abs(float(r['alpha_gross_minus_displayed'])),abs(float(r['beta_gross_minus_displayed'])))
    assert float(r['cross_alpha_on_B1_B2_abs'])==0
    assert float(r['cross_beta_on_A1_abs'])==0
assert sorted(counts.values())==[3]*6,counts
assert sum(r['M_is_sigma_pi_proxy']=='True' for r in rows)==12
assert sum(r['M_is_sigma_pi_proxy']=='False' for r in rows)==6
assert sum(float(r['occupation'])==0.5 for r in rows)==4
assert math.isclose(max_delta,0.0345,abs_tol=1e-8)
print('DERIVED_PUBLIC_VALIDATION=PASS; records=18; reference_states=3; bases=2; conditional_proxies=12; transverse_controls=6; fractional_occupation=4; max_abs_displayed_AO_residual=0.0345')
print('RAW_PROVENANCE=NOT_TESTED in public-only mode; PHYSICAL_MODEL_VALIDATION=NOT_TESTED')
