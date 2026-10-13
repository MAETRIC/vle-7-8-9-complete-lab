pipeline {
 agent any
 environment { KUBECONFIG='/etc/kubernetes/lab.kubeconfig' }
 stages {
  stage('Checkout GitHub') { steps { checkout scm } }
  stage('Build and test') { steps { sh 'docker run --rm -v "$WORKSPACE:/app" -w /app node:22-alpine node --test; docker build -t vle-clinic:1 .' } }
  stage('SonarQube SAST') { steps { sh '/opt/vle/scan-sonar.sh "$WORKSPACE"' } }
  stage('Trivy full image scan') { steps { sh 'trivy image --scanners vuln --format json --output trivy-report.json vle-clinic:1; trivy image --scanners vuln --format table vle-clinic:1 > trivy-report.txt; trivy image --scanners vuln --severity CRITICAL --exit-code 1 vle-clinic:1' } }
  stage('Deploy securely') { steps { sh 'sudo -u ubuntu /usr/local/bin/minikube image load vle-clinic:1; kubectl apply -f experiment-9-access.yaml; kubectl apply -f experiment-9.yaml; kubectl -n vle9 rollout status deploy/clinic --timeout=180s' } }
  stage('RBAC validation') { steps { sh '/opt/vle/rbac-checks.sh' } }
  stage('OWASP ZAP baseline') { steps { sh '/opt/vle/scan-zap.sh "$WORKSPACE"' } }
 }
 post { always { archiveArtifacts artifacts:'trivy-report.*,zap-report.*', allowEmptyArchive:true } }
}
