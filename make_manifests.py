from pathlib import Path
import json
B=Path(__file__).parent
(B/'k8s').mkdir(exist_ok=True)
def namespace(n):return {'apiVersion':'v1','kind':'Namespace','metadata':{'name':n}}
def deployment(n,name,version,replicas=2):
 labels={'app':'clinic','version':version}
 return {'apiVersion':'apps/v1','kind':'Deployment','metadata':{'name':name,'namespace':n},'spec':{'replicas':replicas,'selector':{'matchLabels':labels},'template':{'metadata':{'labels':labels},'spec':{'automountServiceAccountToken':False,'serviceAccountName':'clinic-reader' if n=='vle9' else 'default','securityContext':{'runAsNonRoot':True,'runAsUser':1000,'runAsGroup':1000,'seccompProfile':{'type':'RuntimeDefault'}},'containers':[{'name':'clinic','image':'vle-clinic:1','imagePullPolicy':'Never','env':[{'name':'APP_VERSION','value':version},{'name':'EXPERIMENT','value':n[-1]}]+([{'name':x,'valueFrom':{'secretKeyRef':{'name':'clinic-secrets','key':x}}} for x in ['APP_PASSWORD','API_TOKEN']] if n=='vle9' else []),'ports':[{'containerPort':8080,'name':'http'}],'readinessProbe':{'httpGet':{'path':'/healthz','port':8080},'initialDelaySeconds':2,'periodSeconds':2},'livenessProbe':{'httpGet':{'path':'/healthz','port':8080},'initialDelaySeconds':5,'periodSeconds':10},'securityContext':{'allowPrivilegeEscalation':False,'readOnlyRootFilesystem':True,'capabilities':{'drop':['ALL']}},'resources':{'requests':{'cpu':'20m','memory':'32Mi'},'limits':{'cpu':'250m','memory':'96Mi'}}}]}}}}
def service(n,version=None,nodeport=None):
 return {'apiVersion':'v1','kind':'Service','metadata':{'name':'clinic','namespace':n,'labels':{'app':'clinic'}},'spec':{'type':'NodePort' if nodeport else 'ClusterIP','selector':{'app':'clinic',**({'version':version} if version else {})},'ports':[{'name':'http','port':8080,'targetPort':'http',**({'nodePort':nodeport} if nodeport else {})}]}}
def write(n,docs):
 for d in docs:
  if d.get('kind')=='Deployment':
   d['spec']['template']['spec']['containers'][0]['env'] += [{'name':v,'valueFrom':{'secretKeyRef':{'name':'lab-identity','key':v}}} for v in ['STUDENT_NAME','STUDENT_ID']]
 (B/'k8s'/n).write_text('\n---\n'.join(json.dumps(d,indent=2) for d in docs))
write('experiment-7.yaml',[namespace('vle7'),deployment('vle7','clinic','v1-monitored'),service('vle7',nodeport=30081)])
write('experiment-8-blue.yaml',[namespace('vle8'),deployment('vle8','clinic-blue','v1-blue'),service('vle8','v1-blue',30082)])
write('experiment-8-green.yaml',[deployment('vle8','clinic-green','v2-green')])
rbac=[namespace('vle9'),{'apiVersion':'v1','kind':'ServiceAccount','metadata':{'name':'clinic-reader','namespace':'vle9'}},{'apiVersion':'rbac.authorization.k8s.io/v1','kind':'Role','metadata':{'name':'pod-reader','namespace':'vle9'},'rules':[{'apiGroups':[''],'resources':['pods'],'verbs':['get','list','watch']}]},{'apiVersion':'rbac.authorization.k8s.io/v1','kind':'RoleBinding','metadata':{'name':'clinic-reader','namespace':'vle9'},'roleRef':{'apiGroup':'rbac.authorization.k8s.io','kind':'Role','name':'pod-reader'},'subjects':[{'kind':'ServiceAccount','name':'clinic-reader','namespace':'vle9'}]}]
write('experiment-9-access.yaml',rbac)
write('experiment-9.yaml',[deployment('vle9','clinic','v3-secure'),service('vle9',nodeport=30083)])
write('service-monitors.yaml',[{'apiVersion':'monitoring.coreos.com/v1','kind':'ServiceMonitor','metadata':{'name':'clinic','namespace':n,'labels':{'release':'monitoring'}},'spec':{'selector':{'matchLabels':{'app':'clinic'}},'endpoints':[{'port':'http','path':'/metrics','interval':'10s'}]}} for n in ['vle7','vle8','vle9']])
rules=[
 {'alert':'VLEPodFailure','expr':'kube_pod_container_status_waiting_reason{namespace="vle7",reason="CrashLoopBackOff"} == 1','for':'15s','labels':{'severity':'critical','experiment':'7'},'annotations':{'summary':'Experiment 7: a real test pod is in CrashLoopBackOff'}},
 {'alert':'VLEHighCPU','expr':'sum(rate(container_cpu_usage_seconds_total{namespace="vle7",container!="",container!="POD"}[1m])) > 0.3','for':'30s','labels':{'severity':'warning','experiment':'7'},'annotations':{'summary':'Experiment 7: namespace CPU exceeds 0.3 cores during controlled load'}},
 {'alert':'VLENodeDown','expr':'kube_node_status_condition{condition="Ready",status="true"} == 0','for':'1m','labels':{'severity':'critical','experiment':'7'},'annotations':{'summary':'Kubernetes node is not Ready'}},
 {'alert':'VLEFailedLogins','expr':'sum(increase(vle_failed_logins_total{namespace="vle9"}[3m])) > 3','for':'10s','labels':{'severity':'critical','experiment':'9'},'annotations':{'summary':'Experiment 9: repeated failed application logins detected'}},
 {'alert':'VLEUnauthorizedAccess','expr':'sum(increase(vle_unauthorized_total{namespace="vle9"}[3m])) > 3','for':'10s','labels':{'severity':'critical','experiment':'9'},'annotations':{'summary':'Experiment 9: repeated unauthorized API requests detected'}}]
write('alert-rules.yaml',[{'apiVersion':'monitoring.coreos.com/v1','kind':'PrometheusRule','metadata':{'name':'vle-alerts','namespace':'monitoring','labels':{'release':'monitoring'}},'spec':{'groups':[{'name':'vle-experiment-alerts','rules':rules}]}}])
print('Experiment manifests written')
