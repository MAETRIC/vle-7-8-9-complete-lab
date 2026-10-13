#!/bin/bash
set -eu
export KUBECONFIG=/etc/kubernetes/lab.kubeconfig
echo 'ALLOW: list pods as clinic-reader'
kubectl auth can-i list pods --as=system:serviceaccount:vle9:clinic-reader -n vle9
echo 'DENY: read secrets as clinic-reader'
if kubectl auth can-i get secrets --as=system:serviceaccount:vle9:clinic-reader -n vle9; then exit 1; fi
echo 'DENY: delete deployments as clinic-reader'
if kubectl auth can-i delete deployments --as=system:serviceaccount:vle9:clinic-reader -n vle9; then exit 1; fi
echo 'Secret metadata (values are not printed)'
kubectl -n vle9 get secret clinic-secrets
kubectl -n vle9 get role,rolebinding,serviceaccount
echo 'Pod security context'
kubectl -n vle9 get deploy clinic -o jsonpath='{.spec.template.spec.containers[0].securityContext}'
echo
