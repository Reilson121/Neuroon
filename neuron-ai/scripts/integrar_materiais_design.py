"""Vincula os nove PDFs conferidos de Design ao catálogo relacional."""
import json
from pathlib import Path
from app.practice.material_index import catalogo, indexar, permitido
from app.rag.design_corpus import DISCIPLINA, carregar_validado, preparar_material
from app.rag.vector_store import VectorStore


def integrar(store=None):
    dados = carregar_validado()
    store = store or VectorStore()
    materiais, assuntos = catalogo(store, DISCIPLINA)
    esperados = {'local:' + a['pdf'] for a in dados['arquivos']}
    if len(materiais) != 9 or {m['referencia_externa'] for m in materiais} != esperados:
        raise ValueError('Aplique a migration V5 antes de integrar os nove materiais de Design.')
    # Confere todo o lote antes de escrever o primeiro material.
    for material in materiais:
        if permitido(material):
            preparar_material(material, assuntos)

    def assinatura_outras():
        with store._conectar() as c:
            c.execute('SET TRANSACTION READ ONLY')
            return dict(c.execute("""SELECT disciplina, md5(string_agg(
                to_jsonb(c)::text, '' ORDER BY chunk_id)) FROM chunk_documento c
                WHERE disciplina<>%s GROUP BY disciplina""", [DISCIPLINA]).fetchall())
    antes = assinatura_outras()
    resultado = {str(m['id']): indexar(m['id'], store) for m in materiais if permitido(m)}
    if antes != assinatura_outras():
        raise RuntimeError('Outra disciplina mudou durante a integração; confira a base.')
    return {'materiais': resultado, 'outras_disciplinas_preservadas': True}


if __name__ == '__main__':
    resultado = integrar()
    destino = Path(__file__).resolve().parents[1] / 'saidas_testes/design_integracao_materiais.json'
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(resultado, ensure_ascii=True, indent=2))
