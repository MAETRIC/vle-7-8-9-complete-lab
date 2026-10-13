pipeline {
 agent any
 environment { KUBECONFIG='/etc/kubernetes/lab.kubeconfig' }
 triggers { pollSCM('* * * * *') }
 stages {
  stage('Checkout GitHub') { steps { checkout scm } }
  stage('Test and Build') { steps { sh 'docker run --rm -v "$WORKSPACE:/app" -w /app node:22-alpine node --test; docker build -t vle-clinic:1 .' } }
  stage('Load image') { steps { sh 'sudo -u ubuntu /usr/local/bin/minikube image load vle-clinic:1' } }
  stage('Deploy Kubernetes') { steps { sh 'kubectl apply -f experiment-7.yaml; kubectl -n vle7 rollout status deploy/clinic --timeout=180s; kubectl -n vle7 get pods,deploy,svc -o wide' } }
  stage('Verify application') { steps { sh 'curl -fsS http://127.0.0.1:8081/healthz' } }
 }
}
