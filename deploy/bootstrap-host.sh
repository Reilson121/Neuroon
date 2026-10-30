#!/usr/bin/env bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq ca-certificates curl iptables xz-utils python3
if ! command -v docker >/dev/null; then
  version=$(curl -fsSL https://download.docker.com/linux/static/stable/x86_64/ | grep -oE 'docker-[0-9]+\.[0-9]+\.[0-9]+\.tgz' | sort -Vu | tail -1)
  test -n "$version"
  curl -fsSL "https://download.docker.com/linux/static/stable/x86_64/$version" -o /tmp/neuron-docker.tgz
  tar -xzf /tmp/neuron-docker.tgz -C /usr/local/bin --strip-components=1
  cat > /etc/systemd/system/docker.service <<'UNIT'
[Unit]
Description=Docker Engine
After=network-online.target
Wants=network-online.target
[Service]
Type=notify
ExecStart=/usr/local/bin/dockerd --host=unix:///var/run/docker.sock
Restart=always
RestartSec=5
Delegate=yes
LimitNOFILE=1048576
TasksMax=infinity
[Install]
WantedBy=multi-user.target
UNIT
  systemctl daemon-reload
  systemctl enable --now docker
fi
mkdir -p /usr/local/lib/docker/cli-plugins /opt/neuron
chmod 700 /opt/neuron
for repo in compose buildx; do
  if [ "$repo" = compose ]; then asset=docker-compose-linux-x86_64; else asset='buildx-.*linux-amd64$'; fi
  url=$(curl -fsSL "https://api.github.com/repos/docker/$repo/releases/latest" | python3 -c 'import json,sys,re; data=json.load(sys.stdin); pattern=sys.argv[1]; print(next(x["browser_download_url"] for x in data["assets"] if re.fullmatch(pattern,x["name"])))' "$asset")
  curl -fsSL "$url" -o "/usr/local/lib/docker/cli-plugins/docker-$repo"
  chmod 755 "/usr/local/lib/docker/cli-plugins/docker-$repo"
done
mkdir -p /etc/docker
if [ ! -e /etc/docker/daemon.json ]; then
  printf '%s\n' '{"log-driver":"json-file","log-opts":{"max-size":"10m","max-file":"3"}}' > /etc/docker/daemon.json
  systemctl restart docker
fi
docker --version
docker compose version
docker buildx version
