import sys,subprocess,json,requests,collections
stage=sys.argv[1]
def run(args):
 print('$ '+' '.join(args),flush=True);subprocess.run(args,check=False);print(flush=True)
print('\033[2J\033[H',end='');print('VLE live command output - AWS EC2');run(['hostname'])
if stage=='7-pods':
 run(['kubectl','-n','vle7','get','pods','-o','wide'])
 run(['kubectl','-n','vle7','get','deploy,svc'])
 j=requests.get('http://127.0.0.1:9090/api/v1/alerts').json()
 print('PROMETHEUS ALERT API:')
 for a in j['data']['alerts']:
  if a['labels']['alertname'].startswith('VLE'):print(a['labels']['alertname'],a['state'],a['annotations']['summary'])
elif stage=='8-pods':
 run(['kubectl','-n','vle8','get','deploy,pods','-o','wide'])
 run(['kubectl','-n','vle8','get','svc','clinic','-o','wide'])
 run(['kubectl','-n','vle8','get','endpointslices','-l','kubernetes.io/service-name=clinic'])
 run(['curl','-fsS','http://127.0.0.1:8082/healthz'])
elif stage=='9-access':run(['sudo','-u','jenkins','/opt/vle/rbac-checks.sh'])
elif stage=='9-trivy':
 p='/var/lib/jenkins/workspace/Experiment-9/trivy-report.json'
 j=json.loads(subprocess.check_output(['sudo','cat',p]))
 print('TRIVY - COMPLETE IMAGE SCAN');print('Image:',j['ArtifactName'])
 for r in j['Results']:
  print('Target:',r['Target']);print('All-severity vulnerability counts:',dict(collections.Counter(v['Severity'] for v in r.get('Vulnerabilities',[]))))
  for v in r.get('Vulnerabilities',[]):print(v['Severity'],v['VulnerabilityID'],v['PkgName'],v.get('InstalledVersion'),v.get('FixedVersion','No fix available'))
 run(['docker','image','inspect','vle-clinic:1','--format','Runtime user: {{.Config.User}}'])
 print('Complete JSON and text reports retained in Jenkins build artifacts.')
elif stage=='versions':
 for args in [['terraform','version'],['ansible','--version'],['docker','--version'],['kubectl','version'],['helm','version','--short'],['trivy','--version'],['kubectl','get','nodes']]:
  try:run(args)
  except FileNotFoundError:print('Terraform runs from the operator laptop; see terraform-apply.txt.')
