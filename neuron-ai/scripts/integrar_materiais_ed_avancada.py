"""Vincula as três aulas ao catálogo relacional, sem reprocessar os PDFs."""
import json
from pathlib import Path
from app.practice.material_index import catalogo, indexar, permitido
from app.rag.ed_avancada_corpus import DISCIPLINA, carregar_validado
from app.rag.vector_store import VectorStore


def integrar(store=None):
    carregar_validado()  # Valida todos os originais antes da primeira escrita.
    store = store or VectorStore()
    def assinatura_outras():
        with store._conectar() as c:
            c.execute('SET TRANSACTION READ ONLY')
            return dict(c.execute("""SELECT disciplina, md5(string_agg(
                to_jsonb(c)::text, '' ORDER BY chunk_id)) FROM chunk_documento c
                WHERE disciplina<>%s GROUP BY disciplina""", [DISCIPLINA]).fetchall())
    antes = assinatura_outras()
    materiais, _ = catalogo(store, DISCIPLINA)
    if len(materiais) != 3:
        raise ValueError('Aplique a migration V4 antes da integração das três aulas.')
    resultado = {str(m['id']): indexar(m['id'], store) for m in materiais if permitido(m)}
    if antes != assinatura_outras():
        raise RuntimeError('Outra disciplina mudou durante a integração; confira a base.')
    return {'materiais': resultado, 'outras_disciplinas_preservadas': True}


if __name__ == '__main__':
    resultado = integrar()
    destino = Path(__file__).resolve().parents[1] / 'saidas_testes/ed_avancada_integracao_materiais.json'
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(resultado, ensure_ascii=True, indent=2))
