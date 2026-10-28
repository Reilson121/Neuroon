"""Inicialização local. Segredos vêm do .env ignorado pelo Git, nunca da UI."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
from dotenv import load_dotenv

ROOT=Path(__file__).resolve().parents[2]
AI=ROOT/'neuron-ai'

def ambiente():
    load_dotenv(AI/'.env')
    load_dotenv(ROOT/'.env')
    env=os.environ.copy()
    env.setdefault('DB_URL',f"jdbc:postgresql://{env.get('DB_HOST','localhost')}:{env.get('DB_PORT','5432')}/{env.get('DB_NAME','neuron')}")
    env.setdefault('HF_HUB_OFFLINE','1');env.setdefault('TRANSFORMERS_OFFLINE','1')
    java=env.get('JAVA_HOME','')
    if not Path(java,'bin','java.exe').is_file():
        java='C:/Program Files/Java/jdk-23'
        if Path(java,'bin','java.exe').is_file():env['JAVA_HOME']=java
    return env

def main():
    p=argparse.ArgumentParser();p.add_argument('servico',choices=['migrar','backend','ia']);args=p.parse_args()
    env=ambiente()
    if args.servico=='ia':
        if not env.get('NEURON_INTERNAL_TOKEN'):raise SystemExit('Configure NEURON_INTERNAL_TOKEN no .env antes de iniciar.')
        env.setdefault('NEURON_PRELOAD_MONITOR','1')
        comando=[sys.executable,'-B','-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000','--workers','1']
        cwd=AI
    else:
        cwd=ROOT/'backend'/'demo'
        if args.servico=='backend':env.setdefault('NEURON_GUEST_ENABLED','true')
        versao=Path(env.get('JAVA_HOME','')).name.removeprefix('jdk-')
        comando=[str(cwd/'gradlew.bat'),f'-PjavaVersion={versao}', 'migrateLocal' if args.servico=='migrar' else 'bootRun','--offline']
    raise SystemExit(subprocess.call(comando,cwd=cwd,env=env))

if __name__=='__main__':main()
