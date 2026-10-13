#!/bin/bash
set -eu
work=$1
docker run --rm --network host --user "$(id -u):$(id -g)" -e SONAR_USER_HOME=/tmp/.sonar --env-file /opt/vle/sonar.env -v "$work:/usr/src" sonarsource/sonar-scanner-cli:latest -Dsonar.working.directory=/usr/src/.scannerwork -Dsonar.projectKey=vle9-clinic -Dsonar.projectName='VLE 9 Synthetic Clinic' -Dsonar.sources=. -Dsonar.inclusions=server.js -Dsonar.tests=. -Dsonar.test.inclusions=server.test.js -Dsonar.exclusions=server.test.js -Dsonar.scm.disabled=true
