#!/bin/bash
set -Eeuo pipefail
exec > >(tee -a /home/ubuntu/bootstrap.log) 2>&1
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -qq
sudo apt-get install -y ansible
ansible-playbook /home/ubuntu/lab/setup.yml | tee /home/ubuntu/ansible-recap.txt
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
curl -fsSLo /tmp/kubectl https://dl.k8s.io/release/$(curl -fsSL https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl
sudo install -m 755 /tmp/kubectl /usr/local/bin/kubectl
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | sudo bash
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sudo sh -s -- -b /usr/local/bin
PLUGIN_URL=$(curl -fsSL https://api.github.com/repos/jenkinsci/plugin-installation-manager-tool/releases/latest | jq -r '[.assets[] | select(.name | endswith(".jar"))][0].browser_download_url')
curl -fsSL "$PLUGIN_URL" -o /tmp/plugins.jar
sudo java -jar /tmp/plugins.jar --war /usr/share/java/jenkins.war --plugin-download-directory /var/lib/jenkins/plugins --plugins workflow-aggregator git docker-workflow pipeline-stage-view
sudo chown -R jenkins:jenkins /var/lib/jenkins/plugins
sudo -u ubuntu env HOME=/home/ubuntu minikube start --driver=docker --memory=3900 --cpus=2 --kubernetes-version=v1.34.0
sudo mkdir -p /etc/kubernetes
sudo -u ubuntu env HOME=/home/ubuntu kubectl config view --raw --flatten | sudo tee /etc/kubernetes/lab.kubeconfig >/dev/null
sudo chown jenkins:jenkins /etc/kubernetes/lab.kubeconfig
sudo chmod 600 /etc/kubernetes/lab.kubeconfig
echo 'jenkins ALL=(ubuntu) NOPASSWD: /usr/local/bin/minikube' | sudo tee /etc/sudoers.d/vle-jenkins >/dev/null
sudo chmod 440 /etc/sudoers.d/vle-jenkins
sudo docker run -d --name mailpit --restart unless-stopped -p 8025:8025 -p 1025:1025 axllent/mailpit:latest
sudo docker run -d --name sonarqube --restart unless-stopped -p 9000:9000 -e SONAR_ES_JAVAOPTS='-Xms512m -Xmx512m' -e SONAR_WEB_JAVAOPTS='-Xms256m -Xmx512m' sonarqube:community
echo 'BOOTSTRAP COMPLETE'
