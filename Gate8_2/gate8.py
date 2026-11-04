#!/usr/bin/env python3
"""Gate 8: localhost-only, read-only replay of real sealed Gate 7 records.
No network client; no checkout; no AI calls. Python standard library only.
"""
import argparse
import hashlib
import json
import mimetypes
import os
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlsplit, unquote

WORLD_ORDER = 'ABFCDE'
LABELS = {'A':'First view', 'B':'Added second view', 'F':'Untrusted claim', 'C':'Consistent markings', 'D':'Model code absent', 'E':'Wrong pair'}
VALID_ACTIONS = {'ALLOW','REQUEST_MORE_EVIDENCE','HOLD_FOR_REVIEW'}

def sha(data): return hashlib.sha256(data).hexdigest()

def load_json(path): return json.loads(path.read_text(encoding='utf-8-sig'))

def safe_image(root, rel):
    if not isinstance(rel,str) or not rel.startswith('evidence/'):
        raise ValueError('Unsafe photo path')
    target = (root / rel).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError('Missing/outside image')
    if target.suffix.lower() not in ('.jpg','.jpeg','.png','.webp'):
        raise ValueError('Not an allowed image')
    return target

def load_replay(g7, allow_incomplete=False):
    g7 = Path(g7).resolve()
    if not (g7/'manifests/seal.json').is_file(): raise ValueError('Missing Gate 7 seal')
    # Execute actual Gate 7 seal checks using source code, with no network access.
    import importlib.util
    spec = importlib.util.spec_from_file_location('gate7_verified_local',g7/'gate7.py')
    if spec is None or spec.loader is None: raise ValueError('Gate 7 runner not found')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    seal = mod.verify_seal()
    results = load_json(g7/'reports/gate7_results.json')
    if results.get('status')!='COMPLETE_COMPARISON' or results.get('model_evaluated')!=6:
        raise ValueError('Gate 7 results are not complete')
    if results.get('sealed_truth_sha256')!=seal['truth_sha256']:
        raise ValueError('Results truth does not match seal')
    truth = load_json(g7/'manifests/truth.json')['world_actions']
    rows = {r['world']:r for r in results['worlds']}
    if set(rows)!=set('ABCDEF'): raise ValueError('Unexpected worlds in report')
    worlds = []
    for w in WORLD_ORDER:
        item = load_json(g7/f'worlds/{w}.json')
        response_path = g7/f'reports/model_outputs/{w}.json'
        if not response_path.is_file(): raise ValueError(f'Missing imported model output {w}')
        record = load_json(response_path)
        if record.get('world_id')!=w or record.get('action') not in VALID_ACTIONS:
            raise ValueError(f'Invalid model action in {w}')
        if record.get('action')!=rows[w]['model_action'] or truth[w]!=rows[w]['expected']:
            raise ValueError(f'Model/expected mismatch in report for {w}')
        if record.get('model')!='muse-spark-1.3':
            raise ValueError(f'Unexpected model for {w}')
        raw = record.get('raw_response')
        if not isinstance(raw,str): raise ValueError(f'Raw response missing in {w}')
        decoded = json.loads(raw)
        if decoded.get('action') != record['action'] or not isinstance(decoded.get('rationale'),str):
            raise ValueError(f'Raw action/rationale mismatch in {w}')
        photos=[]
        for i,p in enumerate(item['photos']):
            file=safe_image(g7,p['path'])
            if sha(file.read_bytes())!=p['sha256']:
                raise ValueError(f'Photo hash mismatch {w} image {i}')
            photos.append({'url':f'/media/{w}/{i}', 'sha256':p['sha256']})
        worlds.append({'id':w,'title':LABELS[w],'action':record['action'],
          'expected':truth[w],'correct':record['action']==truth[w],
          'rationale':decoded['rationale'], 'raw_sha256':sha(raw.encode('utf-8')),
          'photos':photos,'untrusted_text':item.get('untrusted_text',''),
          'model':record['model'], 'stage':record.get('stage',''),
          'source':'Imported Gate 7 Meta Muse response'})
    return {'status':'VERIFIED_SEALED_REPLAY','seal_truth_sha256':seal['truth_sha256'],
        'seal_sha256':sha(json.dumps(seal,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()),
        'summary':{'model_correct':results['model_correct'],'baseline_correct':results['baseline_correct'],
        'model_evaluated':results['model_evaluated'],'meta_superiority_proven':results.get('meta_superiority_proven',False)},
        'worlds':worlds, 'limits':['No real checkout or enforcement','Policy effects on screen are simulated',
        'Not an authenticity certification','Six selected conditions, not a statistical benchmark',
        'A, B and F reuse the same underlying photographs']}

class Handler(BaseHTTPRequestHandler):
    server_version='RECALLZERO-G8.2/1.0'
    def log_message(self, fmt, *args): pass
    def respond(self, code, payload, mime='application/json; charset=utf-8'):
        body = payload if isinstance(payload,bytes) else json.dumps(payload,ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type',mime)
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'")
        self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        path=unquote(urlsplit(self.path).path)
        if path == '/':
            return self.respond(200,(Path(__file__).parent/'index.html').read_bytes(),'text/html; charset=utf-8')
        if path == '/app.js':
            return self.respond(200,(Path(__file__).parent/'app.js').read_bytes(),'text/javascript; charset=utf-8')
        if path == '/style.css':
            return self.respond(200,(Path(__file__).parent/'style.css').read_bytes(),'text/css; charset=utf-8')
        if path == '/api/replay': return self.respond(200,self.server.replay)
        parts=path.strip('/').split('/')
        if len(parts)==3 and parts[0]=='media' and parts[1] in WORLD_ORDER and parts[2].isdigit():
            w=parts[1]; i=int(parts[2]); item=load_json(self.server.g7/f'worlds/{w}.json')
            if i>=len(item['photos']): return self.respond(404,{'error':'Not found'})
            p=item['photos'][i]
            try:
                image=safe_image(self.server.g7,p['path']); content=image.read_bytes()
                if sha(content)!=p['sha256']: return self.respond(409,{'error':'Evidence changed'})
                mime=mimetypes.guess_type(image)[0] or 'application/octet-stream'
                return self.respond(200,content,mime)
            except ValueError as exc: return self.respond(400,{'error':str(exc)})
        return self.respond(404,{'error':'Not found'})
    def do_POST(self): return self.respond(405,{'error':'Read-only replay: no actions are executed'})

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--gate7',required=True,help='Path to existing sealed Gate 7 project')
    ap.add_argument('--check',action='store_true')
    ap.add_argument('--port',type=int,default=8770)
    args=ap.parse_args()
    data=load_replay(args.gate7)
    print(json.dumps({'status':data['status'],'worlds':[x['id'] for x in data['worlds']], 'score':data['summary'],
     'seal_sha256':data['seal_sha256'],'server_calls':0},indent=2))
    if args.check: return
    server=ThreadingHTTPServer(('127.0.0.1',args.port), Handler)
    server.g7=Path(args.gate7).resolve(); server.replay=data
    print(f'Open http://127.0.0.1:{args.port}  (Ctrl+C to stop)')
    server.serve_forever()

if __name__=='__main__': main()
