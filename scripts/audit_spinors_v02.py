#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Toni Mladenovski (original project contributions)
"""Reproduce CBi/CBi- Dirac-Fock Mulliken spinor mixing summaries.

No ab initio calculation is run. Input: original investigator-provided ZIPs
placed next to this script, or specified via --data-dir.
For the selected axial |m_j|=1/2 valence spinors, the AO tables must
corroborate the mapping: alpha/A1=sigma and beta/B1,B2=pi. The numerical
mapping is NOT valid for arbitrary spinors and is NOT an observable.
"""
import argparse, csv, hashlib, json, re, zipfile
from pathlib import Path

INPUTS = {
    'CBi-': 'CBi_Anion_IPEOMCCSD.zip',
    'CBi(X)': 'CBi_NeutralwithAnionGeometry_X_State_CCSDT.zip',
    'CBi(A)': 'CBi_NeutralwithAnionGeometry_A_State_CCSDT.zip',
}
SELECTED = {'CBi-': (43,44,45), 'CBi(X)': (43,44,45), 'CBi(A)': (43,44,45)}
RX = re.compile(r'^\* Electronic eigenvalue no\.\s*(\d+):\s*([+-]?[\d.]+(?:[Ee][+-]?\d+)?)\s+\(Occupation : f =\s*([\d.]+)\)\s+m_j=\s*(-?\d+/\d+)', re.M)
RX_A = re.compile(r'^\s*alpha\s+([\d.]+)\s*\|', re.M)
RX_B = re.compile(r'^\s*beta\s+([\d.]+)\s*\|', re.M)
HARTREE_TO_EV=27.211386245988

def parse_output(content):
    positions=list(RX.finditer(content))
    out={}
    for i,match in enumerate(positions):
        block=content[match.end():positions[i+1].start() if i+1<len(positions) else len(content)]
        a=RX_A.search(block); b=RX_B.search(block)
        if not (a and b): continue
        num=int(match[1]); energy=float(match[2]); alpha=float(a[1]); beta=float(b[1]); mj=match[4]
        out[num]={'spinor':num,'mj':mj,'occupation':float(match[3]),'energy_hartree':energy,'energy_ev':energy*HARTREE_TO_EV,
                  'alpha_total':alpha,'beta_total':beta,
                  'M':4*alpha*beta,'total':alpha+beta}
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-dir',type=Path,default=Path('.'));ap.add_argument('--out-dir',type=Path,default=Path('.'))
    args=ap.parse_args();args.out_dir.mkdir(parents=True,exist_ok=True)
    rows=[]; provenance=[]
    for state,name in INPUTS.items():
        source=args.data_dir/name
        if not source.is_file(): raise FileNotFoundError(f'Missing {source}; obtain original data independently')
        provenance.append({'file':name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
        with zipfile.ZipFile(source) as z:
            files=[n for n in z.namelist() if n.endswith('.out') and ('/3z/' in n or '/4z/' in n)]
            for member in sorted(files):
                basis='3z' if '/3z/' in member else '4z'
                found=parse_output(z.read(member).decode('latin-1'))
                for num in SELECTED[state]:
                    if num not in found:raise RuntimeError(f'Missing spinor {num} in {member}')
                    rec=found[num]
                    if abs(rec['total']-1.0)>0.001: raise RuntimeError(f'Missing population normalization: {member}: {num}')
                    if rec['mj'] not in ('1/2','-3/2'): raise RuntimeError(f'Unexpected mj: {member}: {num}')
                    rows.append({'state':state,'basis':basis,'source_archive':name,'source_member':member,**rec})
    rows.sort(key=lambda x: (['CBi-','CBi(X)','CBi(A)'].index(x['state']),x['spinor'],x['basis']))
    outfile=args.out_dir/'spinor_audit_v02.csv'
    with outfile.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    (args.out_dir/'input_sha256.json').write_text(json.dumps(provenance,indent=2)+'\n')
    for row in rows:
        print(f"{row['state']:6s} {row['basis']} #{row['spinor']:02d} mj={row['mj']:>4}  sigma={row['alpha_total']:.4f} pi={row['beta_total']:.4f} M={row['M']:.6f}")
    print('\nBasis deltas |M(4z)-M(3z)|:')
    for state in INPUTS:
        for num in SELECTED[state]:
            ms={row['basis']:row['M'] for row in rows if row['state']==state and row['spinor']==num}
            print(f'{state} #{num}: {abs(ms["4z"]-ms["3z"]):.6f}')

if __name__=='__main__':main()
