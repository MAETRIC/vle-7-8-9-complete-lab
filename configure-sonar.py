import requests,json,time,subprocess,os
from pathlib import Path
s=json.loads(Path('/home/ubuntu/private/secrets.json').read_text())
url='http://127.0.0.1:9000'
for _ in range(120):
 try:
  if requests.get(url+'/api/system/status',timeout=5).json().get('status')=='UP':break
 except requests.RequestException:pass
 time.sleep(5)
else:raise RuntimeError('SonarQube did not become ready')
r=requests.post(url+'/api/users/change_password',auth=('admin','admin'),data={'login':'admin','previousPassword':'admin','password':s['sonar']},timeout=20)
auth=('admin',s['sonar'])
r=requests.get(url+'/api/authentication/validate',auth=auth);assert r.json().get('valid'),'Sonar authentication failed'
r=requests.post(url+'/api/projects/create',auth=auth,data={'project':'vle9-clinic','name':'VLE 9 Synthetic Clinic','visibility':'public'});assert r.status_code in [200,400],r.text
r=requests.post(url+'/api/user_tokens/generate',auth=auth,data={'name':'vle-lab-scan','type':'PROJECT_ANALYSIS_TOKEN','projectKey':'vle9-clinic'});r.raise_for_status()
token=r.json()['token']
Path('/home/ubuntu/private/sonar.env').write_text('SONAR_TOKEN='+token+'\nSONAR_HOST_URL=http://127.0.0.1:9000\n')
os.chmod('/home/ubuntu/private/sonar.env',0o600)
subprocess.run(['sudo','cp','/home/ubuntu/private/sonar.env','/opt/vle/sonar.env'],check=True)
subprocess.run(['sudo','chown','jenkins:jenkins','/opt/vle/sonar.env'],check=True)
print('SonarQube app project and project-scoped scanner token configured; token omitted.')
