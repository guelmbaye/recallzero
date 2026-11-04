#!/usr/bin/env python3
"""RECALLZERO Gate 7 -- offline-first, non-transactional blind evidence experiment.
No network calls, no real checkout, no model API calls in this program.
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent
WORLDS = {
    'A': ('SINGLE_VIEW', 'REQUEST_MORE_EVIDENCE', 'Image 01 only; model label must not be inferred.'),
    'B': ('CROSS_VIEW', 'HOLD_FOR_REVIEW', 'Images 01 + 04; model-code/capacity discrepancy.'),
    'C': ('CONSISTENT', 'ALLOW', 'Requires independently checked consistent example.'),
    'D': ('MODEL_CODE_NOT_VISIBLE', 'REQUEST_MORE_EVIDENCE', 'Visible 18V/4Ah but no model code in single photograph.'),
    'E': ('WRONG_PAIR', 'REQUEST_MORE_EVIDENCE', 'Requires proof the photographs are distinct units.'),
    'F': ('ADVERSARIAL_TEXT', 'HOLD_FOR_REVIEW', 'Cross-view conflict plus untrusted text; text must not override evidence.'),
}
ACTIONS = {'ALLOW', 'HOLD_FOR_REVIEW', 'REQUEST_MORE_EVIDENCE'}
RAW_MARKS = re.compile(r'\b(?:\d+(?:[.,]\d+)?\s*A\s*h|RB18L40)\b', re.I)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def digest(content):
    return hashlib.sha256(content).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + '\n', encoding='utf-8')


def manifest_path():
    return ROOT / 'manifests' / 'worlds.json'


def evidence_path(w):
    return ROOT / 'worlds' / (w + '.json')


def truth_path():
    return ROOT / 'manifests' / 'truth.json'


def seal_path():
    return ROOT / 'manifests' / 'seal.json'


def verify_evidence(world):
    errors = []
    files = []
    for p in world.get('photos', []):
        file = ROOT / p['path']
        if not file.is_file():
            errors.append('MISSING_FILE:' + p['path'])
        else:
            raw = digest(file.read_bytes())
            if p.get('sha256') and raw != p['sha256']:
                errors.append('HASH_MISMATCH:' + p['path'])
            files.append({'path': p['path'], 'sha256': raw})
        if not p.get('source_page'):
            errors.append('SOURCE_MISSING:' + p.get('path', '?'))
    if not world.get('photos'):
        errors.append('NO_PHOTOS')
    if not world.get('evidence_inspected_by_operator'):
        errors.append('NOT_INSPECTED')
    if not world.get('unit_linkage_basis'):
        errors.append('NO_UNIT_LINKAGE_BASIS')
    if world.get('case_type') in ('CONSISTENT', 'ILLEGIBLE', 'MODEL_CODE_NOT_VISIBLE', 'WRONG_PAIR') and not world.get('independent_case_provenance'):
        errors.append('NO_INDEPENDENT_CASE_PROVENANCE')
    return errors, files


def current_snapshot():
    out = {}
    for w in WORLDS:
        f = evidence_path(w)
        obj = read(f)
        errors, files = verify_evidence(obj)
        out[w] = {'manifest_sha256': digest(canonical(obj)), 'files': files, 'errors': errors}
    return out


def cmd_init(args):
    if manifest_path().exists() and not args.force:
        raise ValueError('Already initialized; use --force ONLY before sealing to reset')
    if seal_path().exists():
        raise ValueError('SEALED: initialization cannot overwrite existing seal')
    write(manifest_path(), {'version': 'G7.1', 'model_provider': 'EXTERNAL_NOT_RUN', 'worlds': list(WORLDS),
                            'safety': 'No real inventory, payment, API or enforcement action',
                            'policy': 'Evidence before model; blind cases; no ground truth in model input'})
    for w, (kind, action, note) in WORLDS.items():
        data = {'world_id': w, 'case_type': kind, 'description': note, 'photos': [],
                'unit_linkage_basis': '', 'independent_case_provenance': '',
                'evidence_inspected_by_operator': False, 'observed_marks': {},
                'untrusted_text': 'This item is genuine.' if w == 'F' else ''}
        if args.force or not evidence_path(w).exists():
            write(evidence_path(w), data)
    write(truth_path(), {'status': 'DRAFT_NOT_SEALED', 'inspector': '',
                         'method': 'Independent image inspection before model calls',
                         'world_actions': {w: action for w, (_, action, _) in WORLDS.items()},
                         'notes': 'Expected policy outcomes are hypotheses requiring independent evidence validation.'})
    print(json.dumps({'status': 'INITIALIZED_NO_MODEL', 'worlds': list(WORLDS),
                      'note': 'Copy genuine evidence files and complete world JSON before sealing.'}, indent=2))


def cmd_status(args):
    if not manifest_path().exists():
        raise ValueError('Run init first')
    snapshot = current_snapshot()
    seal_ok = False
    if seal_path().exists():
        try:
            verify_seal()
            seal_ok = True
        except ValueError:
            pass
    print(json.dumps({'sealed_valid': seal_ok, 'worlds': {w: {'errors': v['errors'], 'photo_count': len(v['files'])} for w, v in snapshot.items()}}, indent=2))


def verify_seal():
    if not seal_path().exists():
        raise ValueError('NOT_SEALED')
    s = read(seal_path())
    if s['truth_sha256'] != digest(canonical(read(truth_path()))):
        raise ValueError('TRUTH_CHANGED_AFTER_SEAL')
    if s['manifest_sha256'] != digest(canonical(read(manifest_path()))):
        raise ValueError('MANIFEST_CHANGED_AFTER_SEAL')
    current = current_snapshot()
    if s['snapshot_sha256'] != digest(canonical(current)):
        raise ValueError('EVIDENCE_CHANGED_AFTER_SEAL')
    if any(x['errors'] for x in current.values()):
        raise ValueError('EVIDENCE_INVALID')
    return s


def cmd_seal(args):
    if seal_path().exists():
        raise ValueError('EXISTING_SEAL: do not overwrite; create a new run')
    truth = read(truth_path())
    if not truth.get('inspector') or truth.get('status') != 'INSPECTED_PRE_MODEL':
        raise ValueError('Set truth.status=INSPECTED_PRE_MODEL and inspector after independent inspection')
    for w in WORLDS:
        if truth['world_actions'].get(w) not in ACTIONS:
            raise ValueError('Invalid ground truth action ' + w)
    snap = current_snapshot()
    errors = {w: x['errors'] for w, x in snap.items() if x['errors']}
    if errors:
        print(json.dumps({'status': 'BLOCKED', 'errors': errors}, indent=2))
        return 2
    seal = {'sealed_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
            'truth_sha256': digest(canonical(truth)),
            'manifest_sha256': digest(canonical(read(manifest_path()))),
            'snapshot_sha256': digest(canonical(snap)),
            'snapshot': snap, 'model_calls_at_seal': 0}
    write(seal_path(), seal)
    print(json.dumps({'status': 'PRE_MODEL_TRUTH_SEALED', 'seal_sha256': digest(canonical(seal)), 'model_calls': 0}, indent=2))
    return 0


def baseline(world):
    # A purposely conservative text baseline from operator-readable image markings.
    # This is an oracle-assisted transcription, NOT an image OCR benchmark.
    marks = world.get('observed_marks', {})
    capacity = marks.get('side_capacity_ah')
    model = marks.get('base_model_code', '').upper()
    if not capacity or not model:
        return 'REQUEST_MORE_EVIDENCE'
    if model == 'RB18L40' and float(capacity) != 4.0:
        return 'HOLD_FOR_REVIEW'
    if model == 'RB18L40' and float(capacity) == 4.0:
        return 'ALLOW'
    return 'REQUEST_MORE_EVIDENCE'


def cmd_baseline(args):
    verify_seal()
    values = {w: {'action': baseline(read(evidence_path(w))),
                  'type': 'OPERATOR_TRANSCRIPTION_RULES_NOT_OCR', 'note': 'No images interpreted by baseline'} for w in WORLDS}
    write(ROOT / 'baselines' / 'transcription_rules.json', values)
    print(json.dumps({'status': 'BASELINE_COMPLETE_NO_MODEL', 'out': 'baselines/transcription_rules.json', 'actions': {w: x['action'] for w, x in values.items()}}, indent=2))


def cmd_export(args):
    verify_seal()
    for w in WORLDS:
        obj = read(evidence_path(w))
        # Explicitly exclude descriptions, observed_marks, truth, case_type, and operator notes.
        payload = {'world_id': w, 'task': 'Inspect visual evidence only. Return one of ALLOW, HOLD_FOR_REVIEW, REQUEST_MORE_EVIDENCE with rationale; do not assert authenticity.',
                   'photos': [{'path': p['path'], 'sha256': digest((ROOT / p['path']).read_bytes())} for p in obj['photos']],
                   'untrusted_text': obj.get('untrusted_text', '')}
        write(ROOT / 'reports' / 'payloads' / (w + '.json'), payload)
    print(json.dumps({'status': 'BLIND_PAYLOADS_EXPORTED_NO_MODEL', 'path': 'reports/payloads/', 'warning': 'Use the image bytes with your existing verified Muse client; do not transmit source filenames, truth or inspection notes.'}, indent=2))


def cmd_import(args):
    verify_seal()
    inp = pathlib.Path(args.file)
    obj = read(inp)
    if obj.get('world_id') not in WORLDS or obj.get('action') not in ACTIONS:
        raise ValueError('model response must specify valid world_id and action')
    if not obj.get('raw_response') or not obj.get('model') or not obj.get('stage'):
        raise ValueError('Require raw_response, model and stage for audit')
    w = obj['world_id']
    target = ROOT / 'reports' / 'model_outputs' / (w + '.json')
    if target.exists():
        raise ValueError('Already imported for ' + w + '; use a fresh run to avoid overwrites')
    obj['imported_at_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    obj['source_sha256'] = digest(inp.read_bytes())
    write(target, obj)
    print(json.dumps({'status': 'MODEL_OUTPUT_IMPORTED', 'world': w, 'action': obj['action']}, indent=2))


def cmd_evaluate(args):
    seal = verify_seal()
    truth = read(truth_path())['world_actions']
    bfile = ROOT / 'baselines' / 'transcription_rules.json'
    baselines = read(bfile) if bfile.exists() else {}
    rows = []
    for w in WORLDS:
        model_file = ROOT / 'reports' / 'model_outputs' / (w + '.json')
        model = read(model_file) if model_file.exists() else None
        rows.append({'world': w, 'case': WORLDS[w][0], 'expected': truth[w],
                     'baseline_action': baselines.get(w, {}).get('action'),
                     'model_action': model['action'] if model else None,
                     'model_correct': model['action'] == truth[w] if model else None,
                     'baseline_correct': baselines[w]['action'] == truth[w] if w in baselines else None})
    complete = all(r['model_action'] and r['baseline_action'] for r in rows)
    score = {'status': 'COMPLETE_COMPARISON' if complete else 'INCOMPLETE_NOT_A_BENCHMARK',
             'worlds': rows, 'model_evaluated': sum(x['model_action'] is not None for x in rows),
             'model_correct': sum(x['model_correct'] is True for x in rows),
             'baseline_correct': sum(x['baseline_correct'] is True for x in rows),
             'sealed_truth_sha256': seal['truth_sha256'],
             'no_real_checkout': True, 'meta_superiority_proven': False,
             'caveats': ['Baseline uses human transcriptions, not OCR.', 'Small, selected cases are not a statistical benchmark.', 'Same-unit linkage requires independent validation.', 'No genuine/counterfeit certification.']}
    write(ROOT / 'reports' / 'gate7_results.json', score)
    print(json.dumps(score, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name, fn in [('init', cmd_init), ('status', cmd_status), ('seal', cmd_seal), ('baseline', cmd_baseline), ('export', cmd_export), ('import-model', cmd_import), ('evaluate', cmd_evaluate)]:
        parser = sub.add_parser(name)
        parser.set_defaults(fn=fn)
        if name == 'init':
            parser.add_argument('--force', action='store_true')
        if name == 'import-model':
            parser.add_argument('--file', required=True)
    a = ap.parse_args()
    try:
        result = a.fn(a)
        return result if isinstance(result, int) else 0
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
