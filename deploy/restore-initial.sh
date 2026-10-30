#!/usr/bin/env bash
set -euo pipefail
cd /opt/neuron
c() { docker compose --env-file deploy/.env -f deploy/compose.yaml "$@"; }
c up -d db
for attempt in $(seq 1 30); do
  if c exec -T db pg_isready -U neuron -d neuron >/dev/null 2>&1; then break; fi
  sleep 2
done
tables=$(c exec -T db psql -U neuron -d neuron -Atc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'")
if [ "$tables" != 0 ]; then
  echo 'Restauração não executada: o banco já contém tabelas.'
  exit 1
fi
c exec -T db pg_restore -U neuron -d neuron --no-owner --no-privileges --exit-on-error < neuron-initial.dump
c exec -T db psql -U neuron -d neuron -c 'SELECT count(*) AS materiais FROM material; SELECT count(*) AS trechos FROM chunk_documento;'
