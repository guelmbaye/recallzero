"""RECALLZERO G7: strictly offline check of sealed payloads before wiring Muse.
Usage: python gate7_muse_preflight.py
No network, API calls, images modification, or manifest modification.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent
WORLDS = 'ABCDEF'
FORBIDDEN = {'observed_marks','inspection_note','source_page','world_actions',
             'case_type','description','independent_case_provenance',
             'unit_linkage_basis','expected','truth'}
EXPECTED_COUNTS = {'A':1,'B':2,'C':1,'D':1,'E':2,'F':2}


def canonical(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')

def sha(b):
    return hashlib.sha256(b).hexdigest()

def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
    seal_file=ROOT/'manifests/seal.json'
    if not seal_file.is_file():
        raise ValueError('NOT_SEALED')
    seal=load(seal_file)
    # Rely on original runner to validate its exact canonical seal semantics.
    import subprocess
    r=subprocess.run([sys.executable, str(ROOT/'gate7.py'), 'status'],cwd=ROOT,capture_output=True,text=True)
    if r.returncode != 0:
        raise ValueError('GATE7_STATUS_FAILED: '+r.stderr.strip())
    status=json.loads(r.stdout)
    if status.get('sealed_valid') is not True:
        raise ValueError('SEAL_NOT_VALID: '+r.stdout.strip())
    if any(v.get('errors') for v in status.get('worlds',{}).values()):
        raise ValueError('EVIDENCE_INVALID')
    out=[]
    for w in WORLDS:
        p=ROOT/'reports'/'payloads'/f'{w}.json'
        payload=load(p)
        if payload.get('world_id') != w:
            raise ValueError(f'{w}: BAD_WORLD_ID')
        if set(payload) != {'world_id','task','photos','untrusted_text'}:
            raise ValueError(f'{w}: UNEXPECTED_TOP_LEVEL_KEYS')
        if FORBIDDEN.intersection(payload):
            raise ValueError(f'{w}: TOP_LEVEL_LEAK')
        if len(payload['photos']) != EXPECTED_COUNTS[w]:
            raise ValueError(f'{w}: IMAGE_COUNT_MISMATCH')
        if bool(payload['untrusted_text']) != (w=='F'):
            raise ValueError(f'{w}: UNTRUSTED_TEXT_MISMATCH')
        for photo in payload['photos']:
            if set(photo) != {'path','sha256'}:
                raise ValueError(f'{w}: UNEXPECTED_PHOTO_KEYS')
            rel=Path(photo['path'])
            if rel.is_absolute() or '..' in rel.parts:
                raise ValueError(f'{w}: UNSAFE_LOCAL_PATH')
            b=(ROOT/rel).read_bytes()
            if sha(b)!=photo['sha256']:
                raise ValueError(f'{w}: PHOTO_HASH_MISMATCH')
        out.append({'world':w,'photos':len(payload['photos']),
                    'untrusted_text':bool(payload['untrusted_text']),
                    'local_bytes_checked':True})
    print(json.dumps({'status':'MUSE_BRIDGE_OFFLINE_PREFLIGHT_PASS',
                      'note':'Image bytes/hash validated locally. No actual Muse request audited.',
                      'worlds':out,'seal_present':True,
                      'model_calls':0,'network_calls':0,'files_modified':0},indent=2))

if __name__=='__main__':
    try:
        main()
    except Exception as e:
        print(json.dumps({'status':'BLOCKED','reason':str(e)},indent=2))
        sys.exit(1)
