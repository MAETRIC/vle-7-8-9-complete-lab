import json,subprocess,base64
from pathlib import Path
s=json.loads(Path('/home/ubuntu/private/secrets.json').read_text())
subprocess.run(['kubectl','create','namespace','monitoring'],check=False)
def secret(n,name,data):
 obj={'apiVersion':'v1','kind':'Secret','metadata':{'name':name,'namespace':n},'type':'Opaque','stringData':data}
 subprocess.run(['kubectl','apply','-f','-'],input=json.dumps(obj),text=True,check=True,stdout=subprocess.DEVNULL)
secret('monitoring','grafana-admin',{'admin-user':'admin','admin-password':s['grafana']})
secret('vle9','clinic-secrets',{'APP_PASSWORD':s['app'],'API_TOKEN':s['app']})
for n in ['vle7','vle8','vle9']:
 secret(n,'lab-identity',{'STUDENT_NAME':s['student_name'],'STUDENT_ID':s['student_id']})
print('Application and Grafana secrets provisioned; values omitted.')
