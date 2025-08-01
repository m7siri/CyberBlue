#!/bin/bash
set -e  # Exit immediately if a command fails

# === Configuration ===
INSTALL_DIR="$HOME/caldera"
PORT_MAPPING="7009:8888"
LOCAL_YML="$INSTALL_DIR/conf/local.yml"

echo "[+] Starting Caldera installation..."

# Step 1: Clone Caldera repo (official, recursive)
if [ ! -d "$INSTALL_DIR" ]; then
  echo "[+] Cloning MITRE Caldera..."
  git clone --recursive https://github.com/mitre/caldera.git "$INSTALL_DIR"
else
  echo "[*] Caldera already exists at $INSTALL_DIR"
fi

# Step 2: Create full local.yml with all required fields
echo "[+] Creating custom local.yml with 'cyberblue' passwords..."
mkdir -p "$INSTALL_DIR/conf"
cat > "$LOCAL_YML" <<EOF
ability_refresh: 60
api_key_blue: cyberblue
api_key_red: cyberblue
app.contact.dns.domain: mycaldera.caldera
app.contact.dns.socket: 0.0.0.0:8853
app.contact.gist: ""
app.contact.html: /weather
app.contact.http: http://0.0.0.0:8888
app.contact.slack.api_key: ""
app.contact.slack.bot_id: ""
app.contact.slack.channel_id: ""
app.contact.tunnel.ssh.host_key_file: ""
app.contact.tunnel.ssh.host_key_passphrase: ""
app.contact.tunnel.ssh.socket: 0.0.0.0:8022
app.contact.tunnel.ssh.user_name: sandcat
app.contact.tunnel.ssh.user_password: s4ndc4t!
app.contact.ftp.host: 0.0.0.0
app.contact.ftp.port: 2222
app.contact.ftp.pword: caldera
app.contact.ftp.server.dir: ftp_dir
app.contact.ftp.user: caldera_user
app.contact.tcp: 0.0.0.0:7010
app.contact.udp: 0.0.0.0:7011
app.contact.websocket: 0.0.0.0:7012
objects.planners.default: atomic
crypt_salt: cyberblue-salt
encryption_key: cyberblue-key
exfil_dir: /tmp/caldera
reachable_host_traits:
  - remote.host.fqdn
  - remote.host.ip
host: 0.0.0.0
port: 8888
plugins:
  - access
  - atomic
  - compass
  - debrief
  - fieldmanual
  - manx
  - response
  - sandcat
  - stockpile
  - training
reports_dir: /tmp
auth.login.handler.module: default
requirements:
  go:
    command: go version
    type: installed_program
    version: 1.19
  python:
    attr: version
    module: sys
    type: python_module
    version: 3.9.0
users:
  red:
    red: cyberblue
    admin: cyberblue
  blue:
    blue: cyberblue
EOF

# Step 3: Build Docker image
echo "[+] Building Docker image with plugins..."
cd "$INSTALL_DIR" || { echo "[-] Failed to cd into $INSTALL_DIR"; exit 1; }
sudo docker build --build-arg VARIANT=full -t caldera .

# Step 4: Run Caldera in background, remove existing container if needed
HOST_PORT="${PORT_MAPPING%%:*}"
CONTAINER_PORT="${PORT_MAPPING##*:}"

echo "[+] Removing existing container (if any)..."
sudo docker rm -f caldera 2>/dev/null || true

echo "[+] Running Caldera silently on http://localhost:$HOST_PORT ..."
sudo docker run -d \
  --name caldera \
  -p "$HOST_PORT:$CONTAINER_PORT" \
  -v "$LOCAL_YML":/usr/src/app/conf/local.yml \
  caldera > /dev/null 2>&1

echo "[✓] Caldera is running in the background on http://localhost:$HOST_PORT"
