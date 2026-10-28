"""Vincula fontes conferidas ao catálogo e reutiliza o sincronizador existente."""
import json
from pathlib import Path
from app.practice.material_index import catalogo,indexar,permitido
from app.rag.vector_store import VectorStore

def main():
    store=VectorStore()
    def outras_disciplinas():
        with store._conectar() as c:
            c.execute('SET TRANSACTION READ ONLY')
            return dict(c.execute("""SELECT disciplina,md5(string_agg(chunk_id||conteudo||embedding::text||metadata::text,'' ORDER BY chunk_id))
                FROM chunk_documento WHERE disciplina<>'estatistica' GROUP BY disciplina""").fetchall())
    antes=outras_disciplinas()
    materiais,_=catalogo(store)
    resultados={str(m['id']):indexar(m['id'],store) for m in materiais if permitido(m)}
    depois=outras_disciplinas()
    if antes!=depois:raise RuntimeError('Conteúdo de outra disciplina mudou durante a integração.')
    with store._conectar() as c:
        contagens=c.execute("SELECT disciplina,count(*) FROM chunk_documento GROUP BY disciplina ORDER BY disciplina").fetchall()
    result={"materiais":resultados,"contagens_por_disciplina":dict(contagens),"outras_disciplinas_preservadas":True,"assinaturas_outras_disciplinas":depois}
    Path('saidas_testes/estatistica_integracao_materiais.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True,indent=2))

if __name__=='__main__':main()
