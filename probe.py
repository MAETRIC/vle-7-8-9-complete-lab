import requests,time,json,sys
from pathlib import Path
duration=int(sys.argv[1]) if len(sys.argv)>1 else 120
path=Path(sys.argv[2]) if len(sys.argv)>2 else Path('availability.json')
records=[];end=time.monotonic()+duration
while time.monotonic()<end:
 start=time.monotonic()
 try:
  r=requests.get('http://127.0.0.1:8082/healthz',timeout=2)
  records.append({'t':round(time.time(),3),'status':r.status_code,'version':r.json().get('version'),'ms':round((time.monotonic()-start)*1000,1)})
 except Exception as e:records.append({'t':round(time.time(),3),'status':0,'error':str(e)})
 time.sleep(.2)
path.write_text(json.dumps(records,indent=2))
summary={'samples':len(records),'failed':sum(r['status']!=200 for r in records),'versions':sorted(set(r.get('version','error') for r in records)),'max_ms':max(r.get('ms',0) for r in records)}
print(json.dumps(summary,indent=2))
