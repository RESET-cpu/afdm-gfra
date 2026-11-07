import json,pathlib,hashlib,csv,collections,time,psutil
root=pathlib.Path.cwd(); b=root/'result/user_count/data/stmp_500_k60_k80_k100_beta01_20261027'; check=root/'paper/C-STMP/checks/user_count_beta01_500_20261028'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for x in iter(lambda:f.read(2**20),b''): h.update(x)
 return h.hexdigest()
a=read(b/'AUDIT.json'); complete=read(b/'COMPLETE.json'); assert complete['status']=='COMPLETE' and a['status']=='PASS'
for pos,(p,h) in enumerate({**a['files'],**complete['files']}.items()):
 assert sha(p)==h,p
 if pos%10000==0: print('verified',pos,flush=True)
counts=collections.defaultdict(set); n=0
with (b/'per_scene.csv').open(encoding='utf-8-sig',newline='') as f:
 for row in csv.DictReader(f):
  key=(row['method'],int(row['index'])); scene=int(row['scene']); assert scene not in counts[key];counts[key].add(scene);n+=1
assert n==15000 and len(counts)==30 and all(v==set(range(500)) for v in counts.values())
for p in [b/'START.json',*(b/'worker_identity').glob('*.json')]:
 d=read(p)
 try:
  proc=psutil.Process(d['pid']); assert abs(proc.create_time()-d['create_time'])>=.01 or proc.cmdline()!=d['cmdline']
 except psutil.NoSuchProcess:pass
summary=read(b/'SUMMARY.json'); st=[x for x in summary['rows'] if x['method']=='STMP']; assert [x['stopping_reasons'].get('MAX_ITERATIONS',0) for x in st]==[0,0,0,3,14]
result=dict(status='PASS',created_unix=time.time(),complete_sha256=sha(b/'COMPLETE.json'),audit_sha256=sha(b/'AUDIT.json'),audit_file_hashes_rechecked=len(a['files']),complete_file_hashes_rechecked=len(complete['files']),exact_coverage=True,paired_inputs=2500,method_results=15000,main_and_workers_exited=True,stmp_rows=st,nonconverged=summary['nonconverged'],removed_scenes=0,visual_review_pending=True)
(check/'DATA_VALIDATION.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); print('PASS',flush=True)
