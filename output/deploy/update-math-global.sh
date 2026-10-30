#!/usr/bin/env bash
set -euo pipefail
umask 077
cd /opt/neuron
exec 9>deploy/math-update.lock
flock -n 9
compose=(docker compose --env-file deploy/.env -f deploy/compose.yaml)
python3 - <<'PY'
import hashlib,json,tarfile
from pathlib import Path
root=Path('/opt/neuron')
with tarfile.open(root/'math-global-update.tar.gz') as tar:
 manifest=json.load(tar.extractfile('math-global-manifest.json'))
 for name,entry in manifest.items():
  p=root/name
  current=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
  if current!=entry['expected']:raise RuntimeError('Fonte mudou desde a preparação: '+name)
print('FONTES_ANTERIORES_CONFERIDAS',len(manifest),flush=True)
PY
stamp=$(date -u +%Y%m%dT%H%M%SZ)
backup="/opt/neuron/deploy/backups/math-global-${stamp}"
mkdir -p "$backup"
"${compose[@]}" exec -T db pg_dump -U neuron -d neuron --format=custom > "$backup/database.dump"
test -s "$backup/database.dump"
"${compose[@]}" exec -T db pg_restore --list < "$backup/database.dump" > "$backup/database-contents.txt"
"${compose[@]}" exec -T db psql -U neuron -d neuron -At -c "SELECT json_build_object('usuarios',(SELECT coalesce(json_agg(id),'[]') FROM usuario WHERE perfil<>'VISITANTE'),'conversas',(SELECT coalesce(json_agg(c.id),'[]') FROM conversa_monitor c JOIN usuario u ON c.usuario_id=u.id WHERE u.perfil<>'VISITANTE'),'mensagens',(SELECT coalesce(json_agg(m.id),'[]') FROM mensagem_monitor m JOIN conversa_monitor c ON m.conversa_id=c.id JOIN usuario u ON c.usuario_id=u.id WHERE u.perfil<>'VISITANTE'),'materiais',(SELECT count(*) FROM material),'chunks',(SELECT count(*) FROM chunk_documento));" > "$backup/baseline.json"
tar --exclude='__pycache__' -czf "$backup/sources.tar.gz" backend/demo/src/main frontend/src neuron-ai/app docs/CALCULO_COMPUTACAO_I.md
for service in ai web; do
 image=$(docker inspect --format '{{.Image}}' "neuron-${service}-1")
 docker tag "$image" "neuron-${service}:before-math-global-${stamp}"
done
printf '%s\n' "$backup" > math-global-last-backup.txt
echo "BACKUP_PRONTO=$backup"
rollback(){
 echo RESTAURANDO_VERSAO_ANTERIOR
 tar -xzf "$backup/sources.tar.gz" -C /opt/neuron
 for service in ai web; do docker tag "neuron-${service}:before-math-global-${stamp}" "neuron-${service}:latest"; done
 "${compose[@]}" up -d --no-deps --wait --wait-timeout 300 ai web
}
trap 'rollback' ERR
python3 - <<'PY'
import tarfile,hashlib,json
from pathlib import Path
root=Path('/opt/neuron')
with tarfile.open(root/'math-global-update.tar.gz') as tar:
 for m in tar.getmembers():
  if root not in (root/m.name).resolve().parents or not m.isfile():raise ValueError('Entrada inválida.')
 tar.extractall(root)
manifest=json.loads((root/'math-global-manifest.json').read_text())
for name,entry in manifest.items():
 if hashlib.sha256((root/name).read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('Fonte divergente: '+name)
print('PACOTE_CONFERIDO',len(manifest),flush=True)
PY
for service in ai web; do
 "${compose[@]}" build "$service" > "$backup/build-${service}.log" 2>&1
 echo "COMPILADO=$service"
done
"${compose[@]}" up -d --no-deps --wait --wait-timeout 300 ai web
"${compose[@]}" ps --format '{{.Service}} {{.State}} {{.Health}}'
trap - ERR
echo "PUBLICACAO_CONCLUIDA=$backup"
