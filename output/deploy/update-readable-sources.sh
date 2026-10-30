#!/usr/bin/env bash
set -euo pipefail
umask 077
cd /opt/neuron
exec 9>deploy/readable-sources-update.lock
flock -n 9
compose=(docker compose --env-file deploy/.env -f deploy/compose.yaml)
test "$(sha256sum frontend/src/components/Texto.jsx | cut -d' ' -f1)" = 3c3e48fc354c3ba6ad54ff318f53a43f9fa2ab8c855af05bc439267e880c1f33
test "$(sha256sum frontend/src/components/Monitor.jsx | cut -d' ' -f1)" = 339485971056e1ae1dbf61fa3a1b5a6cd952c0f075a9e4b6fa16e3fa17e313c1
for name in referenciasLegiveis.js RespostaMonitor.jsx RespostaMonitor.css; do
 test ! -e "frontend/src/components/$name"
done
stamp=$(date -u +%Y%m%dT%H%M%SZ)
backup="/opt/neuron/deploy/backups/readable-sources-${stamp}"
mkdir -p "$backup"
tar -czf "$backup/sources.tar.gz" frontend/src/components/Texto.jsx frontend/src/components/Monitor.jsx
image=$(docker inspect --format '{{.Image}}' neuron-web-1)
docker tag "$image" "neuron-web:before-readable-sources-${stamp}"
printf '%s\n' "$image" > "$backup/image-id.txt"
printf '%s\n' "$backup" > readable-sources-last-backup.txt
echo "BACKUP_PRONTO=$backup"
python3 - <<'PY'
import hashlib,json,tarfile
from pathlib import Path
root=Path('/opt/neuron')
names={f'frontend/src/components/{n}' for n in ['Texto.jsx','Monitor.jsx','referenciasLegiveis.js','RespostaMonitor.jsx','RespostaMonitor.css']}
with tarfile.open(root/'readable-sources-update.tar.gz') as archive:
 members=archive.getmembers()
 assert {m.name for m in members} == names|{'readable-sources-manifest.json'}
 assert all(m.isfile() and root in (root/m.name).resolve().parents for m in members)
 manifest=json.load(archive.extractfile('readable-sources-manifest.json'))
 assert set(manifest)==names
 for name in names:
  assert hashlib.sha256(archive.extractfile(name).read()).hexdigest()==manifest[name]
 archive.extractall(root)
print('PACOTE_CONFERIDO',len(names))
PY
rollback_sources(){
 tar -xzf "$backup/sources.tar.gz" -C /opt/neuron
 rm -f frontend/src/components/referenciasLegiveis.js frontend/src/components/RespostaMonitor.jsx frontend/src/components/RespostaMonitor.css
}
if ! "${compose[@]}" build web > "$backup/build-web.log" 2>&1; then
 rollback_sources
 tail -n 40 "$backup/build-web.log"
 exit 1
fi
echo INTERFACE_COMPILADA
if ! "${compose[@]}" up -d --no-deps --wait --wait-timeout 60 web; then
 rollback_sources
 docker tag "$image" neuron-web:latest
 "${compose[@]}" up -d --no-deps --wait --wait-timeout 60 web
 echo PUBLICACAO_REVERTIDA
 exit 1
fi
"${compose[@]}" ps --format '{{.Service}} {{.State}} {{.Health}}'
echo FONTES_LEGIVEIS_PUBLICADAS
