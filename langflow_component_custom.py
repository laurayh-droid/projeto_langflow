"""
langflow_component_custom.py - Componente Personalizado para Langflow
Este arquivo contém a definição de componentes customizados em Python prontos
para importação no painel visual do Langflow (Langflow 1.0+ e versões anteriores).

Funcionalidades:
1. Extração de ID de pedido no texto do ticket.
2. Consulta dinâmica ao banco SQLite (pedidos.db).
3. Enriquecimento de contexto com dados de rastreio, previsão de entrega e observações.
4. Geração do prompt estruturado para a LLM.
"""

import json
import sqlite3
import os
import re
from typing import Optional, Dict, Any

# Tentativa de importação compatível com Langflow 1.0+
try:
    from langflow.custom import Component
    from langflow.io import MessageTextInput, Output
    from langflow.schema import Data, Message
    LANGFLOW_V1 = True
except ImportError:
    LANGFLOW_V1 = False


# ============================================================================
# COMPONENTE VISUAL PARA LANGFLOW 1.0+
# ============================================================================
if LANGFLOW_V1:
    class ConsultaPedidoETriagemComponent(Component):
        display_name = "Consulta Pedido & Triagem (SQLite)"
        description = "Extrai ID do pedido no texto do ticket e consulta dados no banco SQLite para subsidiar o LLM."
        icon = "database"
        name = "ConsultaPedidoETriagem"

        inputs = [
            MessageTextInput(
                name="ticket_input",
                display_name="Mensagem do Ticket",
                info="Texto do e-mail ou chamado enviado pelo cliente",
                value="Gostaria de saber o status do meu pedido PED-10423",
            ),
            MessageTextInput(
                name="db_path",
                display_name="Caminho do Banco SQLite",
                info="Caminho do arquivo pedidos.db",
                value="pedidos.db",
            ),
        ]

        outputs = [
            Output(display_name="Prompt Enriquecido", name="prompt_enriquecido", method="gerar_prompt"),
            Output(display_name="Dados do Pedido", name="dados_pedido", method="consultar_pedido_dados"),
        ]

        def _extrair_id(self, texto: str) -> Optional[str]:
            match = re.search(r"(PED-\d{4,6}|#\d{4,6}|\b\d{5}\b)", texto, re.IGNORECASE)
            if match:
                val = match.group(0).upper().replace("#", "")
                if val.isdigit():
                    return f"PED-{val}"
                return val
            return None

        def _consultar_sql(self, pedido_id: str, db_file: str) -> Optional[Dict[str, Any]]:
            if not os.path.exists(db_file):
                # Tenta caminho relativo ao diretório atual
                alt_path = os.path.join(os.getcwd(), db_file)
                if os.path.exists(alt_path):
                    db_file = alt_path
                else:
                    return None

            try:
                conn = sqlite3.connect(db_file)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM pedidos WHERE UPPER(id) = ?", (pedido_id.upper(),))
                row = cursor.fetchone()
                conn.close()
                return dict(row) if row else None
            except Exception:
                return None

        def consultar_pedido_dados(self) -> Data:
            texto = self.ticket_input
            pedido_id = self._extrair_id(texto)
            if pedido_id:
                dados = self._consultar_sql(pedido_id, self.db_path)
                if dados:
                    return Data(data=dados)
            return Data(data={"encontrado": False, "mensagem": "Nenhum pedido localizado."})

        def gerar_prompt(self) -> Message:
            texto = self.ticket_input
            pedido_id = self._extrair_id(texto)
            dados = self._consultar_sql(pedido_id, self.db_path) if pedido_id else None

            if dados:
                info_banco = (
                    f"PEDIDO ENCONTRADO NO BANCO:\n"
                    f"- ID: {dados.get('id')}\n"
                    f"- Cliente: {dados.get('cliente_nome')}\n"
                    f"- Produto: {dados.get('produto')}\n"
                    f"- Status: {dados.get('status')}\n"
                    f"- Rastreio: {dados.get('codigo_rastreio')}\n"
                    f"- Previsão Entrega: {dados.get('previsao_entrega')}\n"
                    f"- Transportadora: {dados.get('transportadora')}\n"
                    f"- Observações Internas: {dados.get('observacoes')}\n"
                )
            else:
                info_banco = "Nenhum pedido identificado no texto ou pedido não localizado no banco."

            prompt_final = (
                f"Analise o chamado a seguir e classifique Sentimento, Urgência e Setor Responsável.\n\n"
                f"TICKET DO CLIENTE:\n{texto}\n\n"
                f"INFORMAÇÕES DE SUPORTE (BANCO DE DADOS):\n{info_banco}\n\n"
                f"Retorne o parecer de triagem com a ação interna e a resposta sugerida ao cliente."
            )
            return Message(text=prompt_final)


# ============================================================================
# CÓDIGO FONTE DIRETO PARA COLAR NO COMPONENTE CUSTOM DO LANGFLOW
# ============================================================================
CODIGO_COMPONENTE_LANGFLOW = '''
from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema import Message
import sqlite3
import re
import os

class TriageDatabaseLookup(Component):
    display_name = "Consulta Banco Pedidos SQLite"
    description = "Consulta dados do pedido e prepara o contexto enriquecido para a LLM de triagem."
    icon = "database"

    inputs = [
        MessageTextInput(
            name="mensagem_ticket",
            display_name="Mensagem do Ticket/Email",
            value="Olá, gostaria de saber do meu pedido PED-10423",
            info="Texto recebido do chamado do cliente"
        ),
        MessageTextInput(
            name="caminho_banco",
            display_name="Arquivo SQLite",
            value="pedidos.db",
            info="Caminho do arquivo de banco de dados SQLite"
        )
    ]

    outputs = [
        Output(display_name="Contexto Enriquecido", name="contexto_enriquecido", method="processar")
    ]

    def processar(self) -> Message:
        texto = self.mensagem_ticket
        match = re.search(r"(PED-\\d{4,6}|#\\d{4,6}|\\b\\d{5}\\b)", texto, re.IGNORECASE)
        pedido_id = match.group(0).upper().replace("#", "") if match else None
        if pedido_id and pedido_id.isdigit():
            pedido_id = f"PED-{pedido_id}"

        db_path = self.caminho_banco
        if not os.path.exists(db_path):
            alt = os.path.join(os.getcwd(), db_path)
            if os.path.exists(alt):
                db_path = alt

        info_db = "Nenhum pedido correspondente encontrado no banco de dados."
        if pedido_id and os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pedidos WHERE UPPER(id) = ?", (pedido_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                d = dict(row)
                info_db = (
                    f"DADOS DO PEDIDO NO BANCO:\\n"
                    f"- ID: {d['id']}\\n"
                    f"- Cliente: {d['cliente_nome']}\\n"
                    f"- Produto: {d['produto']}\\n"
                    f"- Status Atual: {d['status']}\\n"
                    f"- Código Rastreio: {d['codigo_rastreio']}\\n"
                    f"- Previsão Entrega: {d['previsao_entrega']}\\n"
                    f"- Transportadora: {d['transportadora']}\\n"
                    f"- Observações: {d['observacoes']}"
                )

        resultado = (
            f"--- TICKET RECEBIDO ---\\n{texto}\\n\\n"
            f"--- INFORMAÇÕES DO BANCO DE DADOS ---\\n{info_db}\\n"
        )
        return Message(text=resultado)
'''


def get_custom_component_code():
    """Retorna o código-fonte pronto para colar no nó Custom Component do Langflow."""
    return CODIGO_COMPONENTE_LANGFLOW.strip()


if __name__ == "__main__":
    print("Código do componente customizado para o Langflow:")
    print("=" * 60)
    print(get_custom_component_code())
    print("=" * 60)

