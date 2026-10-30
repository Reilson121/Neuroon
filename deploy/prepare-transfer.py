"""Prepara um pacote privado, sem imprimir credenciais, para a VPS do NEURON."""
import os
import secrets
import subprocess
import tarfile
from importlib.metadata import version
from pathlib import Path
from dotenv import dotenv_values

root = Path(__file__).resolve().parents[1]
backup = root / 'deploy/backups'
backup.mkdir(exist_ok=True)
access = root / 'deploy/access'
env = {**dotenv_values(root / 'neuron-ai/.env'), **dotenv_values(root / '.env')}
for key in ['DB_PASSWORD', 'OPENROUTER_API_KEY', 'OPENROUTER_MODEL']:
    if not env.get(key):
        raise RuntimeError(f'Configuração obrigatória ausente: {key}')
packages = ['fastapi', 'uvicorn', 'python-dotenv', 'psycopg', 'openai', 'httpx',
            'langchain-core', 'langchain-community', 'langchain-text-splitters',
            'sentence-transformers', 'transformers', 'pypdf', 'pymupdf', 'python-pptx', 'sympy']
lines = [(f'psycopg[binary]=={version(p)}' if p == 'psycopg' else f'{p}=={version(p)}') for p in packages]
(root / 'deploy/requirements-ai.txt').write_text('\n'.join(lines) + '\n', encoding='utf8')
server_env = access / '.env.server'
if not server_env.exists():
    values = {
        'SITE_ADDRESS': 'neuron-45-159-173-74.sslip.io',
        'DB_PASSWORD': secrets.token_hex(32),
        'NEURON_INTERNAL_TOKEN': secrets.token_hex(32),
        'OPENROUTER_API_KEY': env['OPENROUTER_API_KEY'],
        'OPENROUTER_MODEL': env['OPENROUTER_MODEL'],
    }
    server_env.write_text('\n'.join(k + "='" + v.replace("'", "\\'") + "'" for k, v in values.items()) + '\n', encoding='utf8')
dump = backup / 'neuron-initial.dump'
dump_env = {**os.environ, 'PGPASSWORD': env['DB_PASSWORD']}
subprocess.run([
    r'C:\Program Files\PostgreSQL\18\bin\pg_dump.exe',
    '-h', env.get('DB_HOST', 'localhost'), '-p', env.get('DB_PORT', '5432'),
    '-U', env.get('DB_USER', 'postgres'), '-d', env.get('DB_NAME', 'neuron'),
    '--format=custom', '--no-owner', '--no-privileges', '--file', str(dump)
], env=dump_env, check=True, capture_output=True)
archive = backup / 'neuron-source.tar.gz'
excluded = {'.git', 'node_modules', '.gradle', 'build', 'dist', '__pycache__', 'tmp', '.tmp', '.venv', 'qa'}
folders = ['backend/demo', 'frontend', 'neuron-ai/app', 'neuron-ai/sql', 'neuron-ai/materiais_academicos']
count = 0
with tarfile.open(archive, 'w:gz') as tar:
    for folder in folders:
        for directory, dirs, files in os.walk(root / folder):
            dirs[:] = [d for d in dirs if d not in excluded and not d.startswith('build-')]
            for name in files:
                if name.startswith('.env') or name.endswith(('.pyc', '.zip')):
                    continue
                file = Path(directory) / name
                tar.add(file, arcname=file.relative_to(root).as_posix(), recursive=False)
                count += 1
    for name in ['compose.yaml', 'Caddyfile', 'Dockerfile.backend', 'Dockerfile.ai', 'Dockerfile.web', 'requirements-ai.txt']:
        file = root / 'deploy' / name
        tar.add(file, arcname='deploy/' + name)
    tar.add(root / '.dockerignore', arcname='.dockerignore')
    for name in ['integrar_materiais_ed_basica.py', 'integrar_materiais_calculo.py']:
        file = root / 'neuron-ai/scripts' / name
        tar.add(file, arcname='neuron-ai/scripts/' + name)
print('Pacote:', count, 'arquivos;', round(archive.stat().st_size / 1024**2, 1), 'MiB')
print('Backup:', round(dump.stat().st_size / 1024**2, 1), 'MiB; configuração privada preparada.')
