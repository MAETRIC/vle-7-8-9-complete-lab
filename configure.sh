#!/bin/bash
set -Eeuo pipefail
exec > >(tee -a /home/ubuntu/configure.log) 2>&1
sudo mkdir -p /var/lib/jenkins/init.groovy.d /opt/vle
sudo cp /home/ubuntu/private/01-auth.groovy /var/lib/jenkins/init.groovy.d/
sudo chown -R jenkins:jenkins /var/lib/jenkins/init.groovy.d
sudo cp /home/ubuntu/lab/rbac-checks.sh /home/ubuntu/lab/scan-zap.sh /opt/vle/
sudo chmod 755 /opt/vle/*.sh
sudo systemctl restart jenkins
sudo docker build -t vle-clinic:1 /home/ubuntu/lab
minikube image load vle-clinic:1
kubectl apply -f /home/ubuntu/lab/experiment-7.yaml
kubectl apply -f /home/ubuntu/lab/experiment-8-blue.yaml
kubectl apply -f /home/ubuntu/lab/experiment-9-access.yaml
python3 /home/ubuntu/lab/provision-secrets.py
kubectl apply -f /home/ubuntu/lab/experiment-9.yaml
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace -f /home/ubuntu/lab/monitoring-values.yaml --timeout 12m --wait
kubectl apply -f /home/ubuntu/lab/service-monitors.yaml
kubectl apply -f /home/ubuntu/lab/alert-rules.yaml
MINIKUBE_IP=$(minikube ip)
for PAIR in '3000 30300' '9090 30900' '9093 30903' '8081 30081' '8082 30082' '8083 30083'; do
 read -r HOST_PORT NODE_PORT <<< "$PAIR"
 sudo tee /etc/systemd/system/vle-port-$HOST_PORT.service >/dev/null <<EOF
[Unit]
Description=VLE lab tool port $HOST_PORT
After=network.target docker.service
[Service]
ExecStart=/usr/bin/socat TCP-LISTEN:$HOST_PORT,fork,reuseaddr TCP:$MINIKUBE_IP:$NODE_PORT
Restart=always
[Install]
WantedBy=multi-user.target
EOF
 sudo systemctl daemon-reload
 sudo systemctl enable --now vle-port-$HOST_PORT
done
kubectl get nodes
kubectl get pods -A
echo 'CONFIGURATION COMPLETE'
