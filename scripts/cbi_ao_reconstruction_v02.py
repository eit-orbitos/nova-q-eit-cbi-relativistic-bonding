#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Toni Mladenovski (original project contributions)
"""Independent AO-column parsing and displayed-population reconstruction.

Input: original DIRAC archives and author manifest. Read-only, stdlib only.
Every reported AO sum is based on *displayed, thresholded* columns; the
Gross Total is an independent field in the source output. Their residual
is not interpreted as a physical or computational error.

This script is authored during the 2026-11-09 follow-up audit; it is not
Kimi's original parser and is not a correlated-state calculation.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import zipfile

ARCHIVES = [
    ('CBi-', 'CBi_Anion_IPEOMCCSD.zip'),
    ('CBi(X)', 'CBi_NeutralwithAnionGeometry_X_State_CCSDT.zip'),
    ('CBi(A)', 'CBi_NeutralwithAnionGeometry_A_State_CCSDT.zip'),
]
HEAD = re.compile(
    r'^\* Electronic eigenvalue no\.\s*(?P<num>\d+):\s*'
    r'(?P<energy>[+\-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+\-]?\d+)?)'
    r'.*?\(Occupation\s*:\s*f\s*=\s*(?P<occupation>\d+(?:\.\d+)?)\)'
    r'\s*m_j=\s*(?P<mj>-?\d+/\d+)\s*$', re.M)
AO = re.compile(r'\bL\s+(A1|B1|B2)\s+(Bi|C)\s+([A-Za-z0-9]+)\b')
ROW = re.compile(r'^\s*(alpha|beta)\s+([+\-]?(?:\d+\.\d*|\.\d+))\s*\|\s*(.+?)\s*$', re.M)
SEL = {43, 44, 45}


def sha256(path):
    hasher = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda:fh.read(1 << 18),b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def read_selected(raw, state, basis, member):
    heads = list(HEAD.finditer(raw))
    found = []
    for i, match in enumerate(heads):
        n = int(match['num'])
        if n not in SEL:
            continue
        block = raw[match.end():(heads[i+1].start() if i+1 < len(heads) else len(raw))]
        lines = block.splitlines()
        starts = [k for k,line in enumerate(lines) if re.match(r'^Gross\s+Total\s*\|',line)]
        if len(starts) != 1:
            raise ValueError(f'Expected one Gross Total header, got {len(starts)} in {state} {basis} #{n}')
        header = lines[starts[0]]
        labels = [(x.group(1),x.group(2),x.group(3)) for x in AO.finditer(header.split('|',1)[1])]
        if not labels:
            raise ValueError(f'No AO labels {state} {basis} #{n}')
        rows = {}
        for line in lines[starts[0]+1:starts[0]+6]:
            rm = ROW.match(line)
            if rm:
                kind = rm.group(1)
                if kind in rows:
                    raise ValueError(f'duplicate {kind} in {state} {basis} #{n}')
                vals = [float(x) for x in rm.group(3).split()]
                if len(vals) != len(labels):
                    raise ValueError(f'Count mismatch {state} {basis} #{n}: {len(vals)} vs {len(labels)}')
                rows[kind] = (float(rm.group(2)),vals)
        if set(rows) != {'alpha','beta'}:
            raise ValueError(f'Missing rows {state} {basis} #{n}')
        gross_a,vals_a = rows['alpha']
        gross_b,vals_b = rows['beta']
        displayed_a = sum(vals_a)
        displayed_b = sum(vals_b)
        cross_a = sum(abs(value) for label,value in zip(labels, vals_a) if label[0] != 'A1')
        cross_b = sum(abs(value) for label,value in zip(labels, vals_b) if label[0] == 'A1')
        mj = match['mj']
        expected_labels = {'B1','B2'} if abs(int(mj.split('/')[0])) == 3 else {'A1','B1','B2'}
        actual_labels = {label[0] for label in labels}
        if actual_labels != expected_labels:
            raise ValueError(f'Symmetry set {actual_labels} vs {expected_labels} in {state} {basis} #{n}')
        if cross_a > 1e-8 or cross_b > 1e-8:
            raise ValueError(f'Nonzero displayed AO cross-column values in {state} {basis} #{n}')
        if abs(gross_a+gross_b-1) > 0.001:
            raise ValueError(f'Gross totals not normalized in {state} {basis} #{n}')
        found.append(dict(
          state=state,basis=basis,spinor=n,mj=mj,occupation=float(match['occupation']),
          energy_hartree=float(match['energy']),alpha_gross=gross_a,beta_gross=gross_b,
          displayed_alpha_sum=round(displayed_a,8),displayed_beta_sum=round(displayed_b,8),
          alpha_gross_minus_displayed=round(gross_a-displayed_a,8),
          beta_gross_minus_displayed=round(gross_b-displayed_b,8),
          displayed_AO_columns=len(labels),displayed_symmetries='/'.join(sorted(actual_labels)),
          cross_alpha_on_B1_B2_abs=round(cross_a,8),cross_beta_on_A1_abs=round(cross_b,8),
          M_4_alpha_beta=round(4*gross_a*gross_b,10),
          M_is_sigma_pi_proxy=(abs(int(mj.split('/')[0]))==1),
          member=member))
    if {x['spinor'] for x in found} != SEL or len(found)!=3:
        raise ValueError(f'Expected exactly spinors 43,44,45 in {state} {basis}; got {[x["spinor"] for x in found]}')
    return found


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--data-dir',type=Path,default=Path('/mnt/data'))
    parser.add_argument('--manifest',type=Path,default=None)
    parser.add_argument('--output-dir',type=Path,default=Path('.'))
    args=parser.parse_args()
    manifest = args.manifest or (args.data_dir/'input_sha256.json')
    expected = {x['file']:x['sha256'] for x in json.loads(manifest.read_text())}
    checks = []
    all_rows = []
    raw_hashes = []
    for state,file in ARCHIVES:
        path = args.data_dir/file
        digest = sha256(path)
        if digest != expected.get(file):
            raise ValueError(f'SHA-256 mismatch: {file}')
        checks.append(file)
        with zipfile.ZipFile(path) as z:
            files = sorted(x for x in z.namelist() if x.endswith('.out') and ('/3z/' in x or '/4z/' in x))
            if len(files)!=2:
                raise ValueError(f'Expected 2 .out files in {file}: {files}')
            for member in files:
                basis = '3z' if '/3z/' in member else '4z'
                payload=z.read(member)
                raw_hashes.append({'archive':file,'member':member,'sha256':hashlib.sha256(payload).hexdigest()})
                all_rows.extend(read_selected(payload.decode('latin-1'),state,basis,member))
    all_rows.sort(key=lambda r:(['CBi-','CBi(X)','CBi(A)'].index(r['state']),r['basis'],r['spinor']))
    if len(all_rows)!=18:
        raise ValueError(f'Expected 18 rows, got {len(all_rows)}')
    output=args.output_dir
    output.mkdir(exist_ok=True,parents=True)
    with (output/'CBi_V02_AO_RECONSTRUCTION_18_ROWS.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=all_rows[0].keys());w.writeheader();w.writerows(all_rows)
    summary = {
      'script':'cbi_ao_reconstruction_v02.py',
      'raw_archive_hashes_match_manifest':len(checks),
      'raw_output_members_read':len(raw_hashes),
      'selected_spinor_rows_parsed':len(all_rows),
      'displayed_AO_column_count_valid':18,
      'AO_symmetry_label_patterns_pass':18,
      'displayed_AO_cross_symmetry_zero_rows':sum(r['cross_alpha_on_B1_B2_abs']==0 and r['cross_beta_on_A1_abs']==0 for r in all_rows),
      'max_abs_gross_minus_displayed': max(abs(r[key]) for r in all_rows for key in ('alpha_gross_minus_displayed','beta_gross_minus_displayed')),
      'nonzero_threshold_residual_row_count':sum(any(abs(r[key])>1e-8 for key in ('alpha_gross_minus_displayed','beta_gross_minus_displayed')) for r in all_rows),
      'fractional_occupation_row_count':sum(r['occupation']!=1 for r in all_rows),
      'pure_transverse_control_row_count':sum(not r['M_is_sigma_pi_proxy'] for r in all_rows),
      'raw_output_sha256':raw_hashes,
      'status_note':'Displayed AO sum != Gross Total generally: columns truncated by population threshold; not a reconstruction of missing terms.'
    }
    (output/'CBi_V02_AO_RECONSTRUCTION_SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='raw_output_sha256'},indent=2))

if __name__=='__main__':main()
