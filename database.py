"""
database.py - Módulo de Banco de Dados de Pedidos (SQLite)
Simula o banco de dados corporativo de pedidos de um e-commerce para consulta
do agente de triagem e roteamento de chamados.
"""

import sqlite3
import os
from typing import Optional, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pedidos.db")


def inicializar_banco() -> None:
    """Cria a tabela de pedidos e insere registros de teste caso não existam."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id TEXT PRIMARY KEY,
            cliente_nome TEXT NOT NULL,
            cliente_email TEXT NOT NULL,
            produto TEXT NOT NULL,
            valor REAL NOT NULL,
            data_compra TEXT NOT NULL,
            status TEXT NOT NULL,
            codigo_rastreio TEXT,
            previsao_entrega TEXT,
            transportadora TEXT,
            observacoes TEXT
        )
    """)

    # Pedidos simulados representando diferentes situações reais
    pedidos_iniciais = [
        (
            "PED-10423",
            "Carlos Eduardo Silva",
            "carlos.silva@email.com",
            "Notebook Gamer Ultra 16GB SSD 512GB",
            4899.90,
            "2026-11-05",
            "ATRASADO_EM_TRANSITO",
            "BR987654321BR",
            "2026-11-14",
            "LogExpress Cargas",
            "Mercadoria retida em fiscalização interestadual em 12/11. Nova previsão calculada para 22/11."
        ),
        (
            "PED-10890",
            "Mariana Souza Costa",
            "mariana.costa@empresa.com.br",
            "Smart TV 55 polegadas OLED 4K",
            3750.00,
            "2026-11-18",
            "PAGAMENTO_DUPLICADO_ANALISE",
            None,
            "2026-11-28",
            "DirectLog",
            "Duas cobranças idênticas de R$ 3.750,00 identificadas no gateway de pagamento. Setor de estorno acionado."
        ),
        (
            "PED-10101",
            "Roberto Almeida Santos",
            "roberto.almeida@gmail.com",
            "Cadeira Ergonômica Pro Mesh",
            1280.00,
            "2026-11-01",
            "ENTREGUE",
            "BR123456789BR",
            "2026-11-10",
            "Jadlog",
            "Entregue com sucesso na portaria em 09/11/2026 às 14:32. Recebido pelo porteiro Sr. Manoel."
        ),
        (
            "PED-20340",
            "Juliana Lima Rocha",
            "juliana.rocha@outlook.com",
            "Monitor Profissional 27pol 144Hz",
            1650.00,
            "2026-11-17",
            "EM_SEPARACAO",
            None,
            "2026-11-24",
            "Correios Sedex",
            "Nota fiscal emitida nº 89421. Aguardando coleta da transportadora no centro de distribuição."
        ),
        (
            "PED-30512",
            "Fernando de Castro",
            "fernando.castro@techcorp.com",
            "Servidor NAS 4-Bay 16TB",
            6990.00,
            "2026-11-10",
            "CANCELADO",
            None,
            None,
            None,
            "Pedido cancelado pelo cliente antes do envio em 11/11. Estorno realizado via PIX."
        )
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO pedidos (
            id, cliente_nome, cliente_email, produto, valor, 
            data_compra, status, codigo_rastreio, previsao_entrega, 
            transportadora, observacoes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, pedidos_iniciais)

    conn.commit()
    conn.close()


def consultar_status_pedido(pedido_id: str) -> Optional[Dict[str, Any]]:
    """
    Consulta as informações e status de um pedido no banco de dados SQLite.
    Aceita IDs com ou sem prefixo (ex: '10423', 'PED-10423', '#10423').
    """
    if not pedido_id:
        return None

    # Normalização de ID
    pedido_id_limpo = pedido_id.strip().upper().replace("#", "")
    if not pedido_id_limpo.startswith("PED-") and pedido_id_limpo.isdigit():
        pedido_id_limpo = f"PED-{pedido_id_limpo}"

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pedidos WHERE UPPER(id) = ?", (pedido_id_limpo,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def listar_todos_pedidos():
    """Retorna lista de todos os pedidos para visualização no dashboard/painel."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


if __name__ == "__main__":
    inicializar_banco()
    print("Banco de dados SQLite inicializado com sucesso!")
    print("\nExemplo de consulta para PED-10423:")
    print(consultar_status_pedido("PED-10423"))

