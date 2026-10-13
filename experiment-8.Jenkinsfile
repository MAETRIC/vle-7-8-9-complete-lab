pipeline {
 agent any
 environment { KUBECONFIG='/etc/kubernetes/lab.kubeconfig' }
 stages {
  stage('Checkout GitHub') { steps { checkout scm } }
  stage('Build') { steps { sh 'docker build -t vle-clinic:1 .; sudo -u ubuntu /usr/local/bin/minikube image load vle-clinic:1' } }
  stage('Deploy green') { steps { sh 'kubectl apply -f experiment-8-green.yaml; kubectl -n vle8 rollout status deploy/clinic-green --timeout=180s; kubectl -n vle8 get pods -o wide' } }
  stage('Test green') { steps { sh '''POD=$(kubectl -n vle8 get pod -l version=v2-green -o jsonpath='{.items[0].metadata.name}'); kubectl -n vle8 exec "$POD" -- node -e "fetch('http://localhost:8080/healthz').then(r=>r.json()).then(j=>{console.log(j);if(j.version!=='v2-green')process.exit(1)})"''' } }
  stage('Approve traffic switch') { steps { input message:'Green is healthy. Switch traffic from blue to green?', ok:'Switch to Green' } }
  stage('Switch traffic') { steps { sh 'kubectl -n vle8 patch svc clinic --type merge -p \'{"spec":{"selector":{"app":"clinic","version":"v2-green"}}}\'; kubectl -n vle8 get svc clinic -o wide; curl -fsS http://127.0.0.1:8082/healthz' } }
 }
}
