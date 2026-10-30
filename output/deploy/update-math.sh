#!/usr/bin/env bash
set -euo pipefail
umask 077
cd /opt/neuron
exec 9>deploy/math-update.lock
flock -n 9
compose=(docker compose --env-file deploy/.env -f deploy/compose.yaml)
target=neuron-ai/app/rag/monitor_virtual.py
expected=5945c693e10bcc3bab3989e0c856095288950b378caf06e1f6419abcf38f3901
test "$(sha256sum "$target" | cut -d' ' -f1)" = "$expected"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
backup="/opt/neuron/deploy/backups/math-${stamp}"
mkdir -p "$backup"
cp "$target" "$backup/monitor_virtual.py"
image=$(docker inspect --format '{{.Image}}' neuron-ai-1)
docker tag "$image" "neuron-ai:before-math-${stamp}"
printf '%s\n' "$image" > "$backup/image-id.txt"
printf '%s\n' "$backup" > math-last-backup.txt
echo "BACKUP_PRONTO=$backup"
cp math-monitor-update.py "$target"
if ! "${compose[@]}" build ai > "$backup/build-ai.log" 2>&1; then
 cp "$backup/monitor_virtual.py" "$target"
 tail -n 40 "$backup/build-ai.log"
 exit 1
fi
echo IA_COMPILADA
if ! "${compose[@]}" up -d --no-deps --wait --wait-timeout 300 ai; then
 cp "$backup/monitor_virtual.py" "$target"
 docker tag "$image" neuron-ai:latest
 "${compose[@]}" up -d --no-deps --wait --wait-timeout 300 ai
 echo PUBLICACAO_REVERTIDA
 exit 1
fi
"${compose[@]}" ps --format '{{.Service}} {{.State}} {{.Health}}'
echo PUBLICACAO_MATEMATICA_CONCLUIDA
