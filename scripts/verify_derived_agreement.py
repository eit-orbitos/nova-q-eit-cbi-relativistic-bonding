#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Toni Mladenovski (original project contributions)
"""Compare two previously derived public CSV summaries; NOT a raw-origin validation."""
from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'data'/'spinor_ao_audit_18.csv').open(encoding='utf-8')))
reference=list(csv.DictReader((ROOT/'data'/'independent_spinor_reference_18.csv').open(encoding='utf-8')))
key=lambda r:(r['state'],r['basis'],r['spinor'])
a={key(r):r for r in rows};b={key(r):r for r in reference}
assert len(a)==len(b)==18 and set(a)==set(b)
fields={'alpha_gross':'alpha','beta_gross':'beta','occupation':'occupation',
        'energy_hartree':'energy_hartree','M_4_alpha_beta':'M_spin_proxy','mj':'mj'}
errors=[]
for k in sorted(a):
    for x,y in fields.items():
        ok=a[k][x]==b[k][y] if x=='mj' else abs(float(a[k][x])-float(b[k][y]))<1e-12
        if not ok:errors.append((k,x,a[k][x],b[k][y]))
assert not errors,errors
print('PUBLIC_DERIVED_CROSSCHECK=PASS; rows=18; fields=108; provenance/authenticity/physical_model=NOT_TESTED')
