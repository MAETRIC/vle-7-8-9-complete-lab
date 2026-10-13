# Experiments 7, 8 and 9

Classroom DevOps and DevSecOps demonstrations.

Synthetic classroom application. No real patient information is used.

* Experiment 7: GitHub, Jenkins, Docker, Kubernetes, Prometheus, Grafana and Alertmanager. Alerts are delivered through SMTP to Mailpit, a local test inbox.
* Experiment 8: Terraform and Ansible infrastructure; two ready blue/green deployments; Jenkins tests green, waits for approval, switches traffic; a separate rollback restores blue.
* Experiment 9: actual application analysis in SonarQube, complete Trivy findings, a nonroot container, restricted Kubernetes RBAC, environment secrets, OWASP ZAP, security metrics and alerts.

`make_manifests.py` generates the checked-in Kubernetes manifests. Credentials and Terraform state must never be committed. The Jenkinsfiles assume Jenkins is configured for this repository and that the lab bootstrap has completed. SonarQube tokens and Grafana/app credentials are provisioned privately.

The Trivy pipeline fails for CRITICAL vulnerabilities; all severities remain in its reports. ZAP baseline warnings remain visible and are not represented as a clean scan. This is an isolated teaching deployment, not a production healthcare system.
