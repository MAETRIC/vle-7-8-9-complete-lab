#!/bin/bash
set -eu
touch /home/ubuntu/proof.log
cat > /home/ubuntu/proof-terminal.sh <<'EOF'
#!/bin/bash
printf '\033[2J\033[H'
tail -n 35 -F /home/ubuntu/proof.log
EOF
chmod 755 /home/ubuntu/proof-terminal.sh
sudo tee /etc/systemd/system/vle-terminal.service >/dev/null <<'EOF'
[Unit]
Description=Read-only experiment command output
After=network.target
[Service]
User=ubuntu
ExecStart=/usr/bin/ttyd -R -i 127.0.0.1 -p 7681 -t fontSize=15 /home/ubuntu/proof-terminal.sh
Restart=always
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now vle-terminal
