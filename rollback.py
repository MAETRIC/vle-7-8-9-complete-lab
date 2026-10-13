import subprocess,json
print('\033[2J\033[HExperiment 8 - Rollback to blue',flush=True)
patch=json.dumps({'spec':{'selector':{'app':'clinic','version':'v1-blue'}}})
args=['kubectl','-n','vle8','patch','svc','clinic','--type','merge','-p',patch]
print('$ '+' '.join(args),flush=True);subprocess.run(args,check=True)
subprocess.run(['kubectl','-n','vle8','get','svc','clinic','-o','wide'],check=True)
subprocess.run(['kubectl','-n','vle8','get','endpointslices','-l','kubernetes.io/service-name=clinic'],check=True)
subprocess.run(['curl','-fsS','http://127.0.0.1:8082/healthz'],check=True)
