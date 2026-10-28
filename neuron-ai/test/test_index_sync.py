import copy
import unittest
from unittest.mock import MagicMock, Mock, patch

from app.rag.index_sync import planejar_sincronizacao, sincronizar_indice


DISCIPLINA = "estrutura_de_dados_avancada"


def chunk(identificador="a", texto="AVL balanceada", **extras):
    return {
        "chunk_id": identificador, "conteudo": texto,
        "metadata": {
            "periodo": "03", "disciplina": DISCIPLINA,
            "assunto": "avl", "aula": "02", "arquivo": "Aula_2.pdf",
            "pagina": 84, "tipo_arquivo": "pdf", "tipo_extracao": "textual",
            "chunk_index": 1, **extras,
        },
    }


class IndexSyncTest(unittest.TestCase):
    def setUp(self):
        self.esperados = [chunk(paginas_mescladas=[83])]
        self.atuais = [chunk(texto="AVL"), chunk("obsoleto", "Título")]
        self.store = Mock()
        self.store.dimensao = 384
        self.store._vetor_para_texto.return_value = "[1,0]"
        self.leitura = MagicMock()
        self.escrita = MagicMock()
        for conexao in (self.leitura, self.escrita):
            conexao.__enter__.return_value = conexao
            conexao.execute.return_value.rowcount = 1
        self.store._conectar.side_effect = [self.leitura, self.escrita]
        self.embedder = Mock()
        self.embedder.dimensions = 384
        self.embedder.gerar_embedding.return_value = [1.0, 0.0]

    def escritas(self):
        return [
            chamada for chamada in self.escrita.execute.call_args_list
            if chamada.args[0].lstrip().startswith(("UPDATE", "DELETE"))
        ]

    def test_plano_distingue_textos_metadados_e_remocoes(self):
        esperados = self.esperados + [chunk("b", paginas_mescladas=[82])]
        atuais = self.atuais + [chunk("b")]
        plano = planejar_sincronizacao(esperados, atuais, DISCIPLINA)
        self.assertEqual(plano["remover"], ["obsoleto"])
        self.assertEqual(plano["atualizar"], ["a", "b"])
        self.assertEqual(plano["recalcular"], ["a"])

    def test_docx_exige_numero_questao_quando_nao_ha_pagina_estavel(self):
        valido=chunk(pagina=None,tipo_arquivo="docx",numero_questao="7")
        planejar_sincronizacao([valido],[valido],DISCIPLINA)
        with self.assertRaises(ValueError):
            planejar_sincronizacao([chunk(pagina=None)],[],DISCIPLINA,True)

    @patch("app.rag.index_sync.ler_chunks")
    def test_filtro_por_arquivo_nao_le_outros_materiais(self,ler):
        ler.return_value=self.esperados
        sincronizar_indice(self.store,self.esperados,DISCIPLINA,tipos_material=None,arquivos=["Aula_2.pdf"])
        ler.assert_called_once_with(self.leitura,DISCIPLINA,None,["Aula_2.pdf"])

    @patch("app.rag.index_sync.ler_chunks")
    def test_insercao_inicial_opt_in_e_conferencia_na_mesma_transacao(self, ler):
        ler.side_effect = [[], [], self.esperados]
        resumo = sincronizar_indice(self.store, self.esperados, DISCIPLINA,
                                   self.embedder, permitir_insercao=True)
        self.assertEqual(resumo["inseridos"], 1)
        self.assertEqual(resumo["embeddings_recalculados"], 1)
        inserts = [c for c in self.escrita.execute.call_args_list
                   if c.args[0].lstrip().startswith("INSERT")]
        self.assertEqual(len(inserts), 1)
        self.assertEqual(inserts[0].args[1][0], "a")
        self.assertEqual(inserts[0].args[1][4], DISCIPLINA)
        self.assertNotIn("ON CONFLICT", inserts[0].args[0])
        self.escrita.__exit__.assert_called_once_with(None, None, None)

    @patch("app.rag.index_sync.ler_chunks")
    def test_falha_na_conferencia_de_insercao_provoca_rollback(self, ler):
        ler.side_effect = [[], [], []]
        with self.assertRaises(RuntimeError):
            sincronizar_indice(self.store, self.esperados, DISCIPLINA,
                              self.embedder, permitir_insercao=True)
        self.assertIs(self.escrita.__exit__.call_args.args[0], RuntimeError)

    def test_rejeita_json_vazio_ids_ausentes_e_arquivos_fora_do_escopo(self):
        outra_disciplina = chunk(disciplina="outra")
        outro_arquivo = chunk("externo", arquivo="Arquivo_novo.pdf")
        for esperados, atuais in [
            ([], self.atuais), (self.esperados, []),
            (self.esperados, self.atuais + [outro_arquivo]),
            (self.esperados, self.atuais + [outra_disciplina]),
            ([outra_disciplina], self.atuais),
        ]:
            with self.subTest(esperados=esperados, atuais=atuais):
                with self.assertRaises(ValueError):
                    planejar_sincronizacao(esperados, atuais, DISCIPLINA)

    @patch("app.rag.index_sync.ler_chunks")
    def test_atualiza_e_remove_apenas_ids_planejados_na_mesma_transacao(self, ler):
        ler.side_effect = [self.atuais, self.atuais, self.esperados]
        resumo = sincronizar_indice(self.store, self.esperados, DISCIPLINA, self.embedder)
        self.assertEqual(resumo["removidos"], 1)
        self.assertEqual(resumo["embeddings_recalculados"], 1)
        self.embedder.gerar_embedding.assert_called_once_with("AVL balanceada")
        update, delete = self.escritas()
        self.assertEqual(update.args[1][-2:], (DISCIPLINA, "a"))
        self.assertEqual(delete.args[1], [DISCIPLINA, ["obsoleto"]])
        self.escrita.__exit__.assert_called_once_with(None, None, None)

    @patch("app.rag.index_sync.ler_chunks")
    def test_mudanca_so_de_metadados_preserva_embedding_e_campo_extra(self, ler):
        atuais = [chunk(campo_extra="preservado")]
        ler.side_effect = [atuais, atuais, self.esperados]
        resumo = sincronizar_indice(self.store, self.esperados, DISCIPLINA, self.embedder)
        self.assertEqual(resumo["embeddings_recalculados"], 0)
        self.embedder.gerar_embedding.assert_not_called()
        update = self.escritas()[0]
        self.assertIsNone(update.args[1][1])
        self.assertEqual(update.args[1][-3].obj["campo_extra"], "preservado")
        self.assertEqual(update.args[1][-3].obj["paginas_mescladas"], [83])

    @patch("app.rag.index_sync.ler_chunks")
    def test_repeticao_nao_escreve_nem_recalcula(self, ler):
        ler.return_value = copy.deepcopy(self.esperados)
        resumo = sincronizar_indice(self.store, self.esperados, DISCIPLINA, self.embedder)
        self.assertEqual(resumo["atualizados"], 0)
        self.store._conectar.assert_called_once()
        self.embedder.gerar_embedding.assert_not_called()

    @patch("app.rag.index_sync.ler_chunks")
    def test_falha_no_embedding_nao_abre_transacao_de_escrita(self, ler):
        ler.return_value = self.atuais
        self.embedder.gerar_embedding.side_effect = RuntimeError("Modelo indisponível")
        with self.assertRaises(RuntimeError):
            sincronizar_indice(self.store, self.esperados, DISCIPLINA, self.embedder)
        self.store._conectar.assert_called_once()
        self.assertEqual(self.escritas(), [])

    @patch("app.rag.index_sync.ler_chunks")
    def test_mudanca_concorrente_interrompe_antes_de_escrever(self, ler):
        ler.side_effect = [self.atuais, self.atuais + [chunk("novo")]]
        with self.assertRaises(RuntimeError):
            sincronizar_indice(self.store, self.esperados, DISCIPLINA, self.embedder)
        self.assertEqual(self.escritas(), [])
        self.assertIs(self.escrita.__exit__.call_args.args[0], RuntimeError)

    @patch("app.rag.index_sync.ler_chunks")
    def test_falha_na_conferencia_final_sai_com_excecao_para_rollback(self, ler):
        ler.side_effect = [self.atuais, self.atuais, self.atuais]
        with self.assertRaises(RuntimeError):
            sincronizar_indice(self.store, self.esperados, DISCIPLINA, self.embedder)
        self.assertIs(self.escrita.__exit__.call_args.args[0], RuntimeError)


if __name__ == "__main__":
    unittest.main()
