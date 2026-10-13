#!/bin/bash
set -eu
work=$1
chmod a+w "$work"
set +e
docker run --rm --network host -v "$work:/zap/wrk:rw" ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://127.0.0.1:8083 -r zap-report.html -J zap-report.json -m 1
result=$?
set -e
echo "ZAP baseline exit code: $result (0=pass, 1=FAIL, 2=WARN)"
test "$result" -le 2
