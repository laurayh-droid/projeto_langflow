"""
test_agent.py - Suíte de Testes Práticos e Análise de Resultados
Valida o funcionamento do agente de triagem e roteamento de chamados sob diferentes
cenários do mundo real (Sentimentos, Urgências, Setores e Consultas de Banco de Dados).
"""

import time
import json
from langchain_agent import AgenteTriagemLangChain

# Conjunto de dados de teste (Casos de uso reais)
CASOS_DE_TESTE = [
    {
        "id": 1,
        "titulo": "Atraso Crítico em Entrega de Hardware",
        "ticket": (
            "De: carlos.silva@email.com\n"
            "Assunto: CADÊ MEU NOTEBOOK??? PEDIDO ATRASADO!\n"
            "Mensagem: Estou extremamente irritado e FURIOSO! Comprei o notebook no pedido #10423 "
            "com promessa de entrega até dia 14/11. Já se passaram vários dias e nada de chegar! "
            "Trabalho com isso e estou tomando prejuízo diário. Se não resolverem hoje mesmo, "
            "vou abrir reclamação no Procon e acionar meu advogado!"
        ),
        "esperado": {
            "sentimento": "NEGATIVO",
            "urgencia": "CRITICA",
            "setor": "LOGISTICA",
            "deve_conter_id": "PED-10423",
            "deve_encontrar_banco": True
        }
    },
    {
        "id": 2,
        "titulo": "Cobrança Duplicada no Cartão de Crédito",
        "ticket": (
            "De: mariana.costa@empresa.com.br\n"
            "Assunto: Cobrança indevida em duplicidade - Pedido PED-10890\n"
            "Mensagem: Olá equipe, verifiquei minha fatura do cartão hoje e notei que a Smart TV 55 pol "
            "do pedido PED-10890 foi cobrada duas vezes no valor de R$ 3.750,00. "
            "Solicito com urgência o estorno da segunda cobrança, pois comprometeu o limite corporativo."
        ),
        "esperado": {
            "sentimento": "NEGATIVO",
            "urgencia": "ALTA",
            "setor": "FINANCEIRO",
            "deve_conter_id": "PED-10890",
            "deve_encontrar_banco": True
        }
    },
    {
        "id": 3,
        "titulo": "Falha Técnica / Crash no Sistema",
        "ticket": (
            "De: suporte.dev@techlabs.io\n"
            "Assunto: Erro 500 e crash na inicialização do aplicativo\n"
            "Mensagem: Boa tarde. Após a última atualização do software para a versão 3.4, "
            "o aplicativo começou a apresentar tela preta com crash constante ao tentar realizar o login. "
            "Estamos com a operação de 5 analistas paralisada devido a este bug."
        ),
        "esperado": {
            "sentimento": "NEGATIVO",
            "urgencia": "ALTA",
            "setor": "SUPORTE_TECNICO",
            "deve_conter_id": None,
            "deve_encontrar_banco": False
        }
    },
    {
        "id": 4,
        "titulo": "Cotação Comercial para Compra Corporativa em Lote",
        "ticket": (
            "De: compras@inovasolucoes.com.br\n"
            "Assunto: Cotação de 50 Monitores 27pol para novo escritório\n"
            "Mensagem: Prezados, bom dia! Estamos reformando nosso escritório central e gostaríamos de "
            "solicitar um orçamento para a aquisição de um lote de 50 monitores profissionais de 27 polegadas. "
            "Vocês oferecem faturamento direto para pessoa jurídica e desconto progressivo por quantidade?"
        ),
        "esperado": {
            "sentimento": "NEUTRO", # ou POSITIVO
            "urgencia": "BAIXA",
            "setor": "COMERCIAL",
            "deve_conter_id": None,
            "deve_encontrar_banco": False
        }
    },
    {
        "id": 5,
        "titulo": "Elogio de Entrega com Solicitação de 2ª Via de NF",
        "ticket": (
            "De: roberto.almeida@gmail.com\n"
            "Assunto: Elogio de entrega rápida e dúvida sobre Nota Fiscal #10101\n"
            "Mensagem: Olá! Gostaria de parabenizar toda a equipe, a Cadeira Ergonômica do pedido #10101 "
            "chegou super rápido e o produto é excelente! Adorei a qualidade. "
            "Poderiam apenas me reenviar a segunda via da nota fiscal por e-mail para fins de declaração?"
        ),
        "esperado": {
            "sentimento": "POSITIVO",
            "urgencia": "MEDIA", # ou BAIXA
            "setor": "FINANCEIRO",
            "deve_conter_id": "PED-10101",
            "deve_encontrar_banco": True
        }
    }
]


def executar_testes_e_analise():
    print("=" * 80)
    print("   BATERIA DE TESTES PRÁTICOS: AGENTE DE TRIAGEM E ROTEAMENTO (LANGFLOW/LANGCHAIN)")
    print("=" * 80)
    
    agente = AgenteTriagemLangChain()
    
    total_testes = len(CASOS_DE_TESTE)
    acertos_sentimento = 0
    acertos_urgencia = 0
    acertos_setor = 0
    acertos_banco = 0
    
    resultados_detalhados = []
    
    inicio_geral = time.time()
    
    for caso in CASOS_DE_TESTE:
        print(f"\n--- [TESTE {caso['id']}] {caso['titulo']} ---")
        t0 = time.time()
        res = agente.processar_ticket(caso["ticket"])
        latencia_ms = (time.time() - t0) * 1000
        
        triagem = res["triagem"]
        banco = res["consulta_banco"]
        esperado = caso["esperado"]
        
        # Validação de Sentimento
        ok_sent = (triagem["sentimento"] == esperado["sentimento"])
        if ok_sent:
            acertos_sentimento += 1
            
        # Validação de Urgência (aceita margem próxima em casos neutros/elogios)
        ok_urg = (triagem["urgencia"] == esperado["urgencia"])
        if ok_urg:
            acertos_urgencia += 1
            
        # Validação de Setor
        ok_setor = (triagem["setor_responsavel"] == esperado["setor"])
        if ok_setor:
            acertos_setor += 1
            
        # Validação do Banco
        ok_banco = (banco["encontrado"] == esperado["deve_encontrar_banco"])
        if ok_banco:
            acertos_banco += 1
            
        print(f"• Sentimento Detectado:  {triagem['sentimento']:<10} | Esperado: {esperado['sentimento']:<10} {'[OK]' if ok_sent else '[DIF]'}")
        print(f"• Urgência Detectada:    {triagem['urgencia']:<10} | Esperado: {esperado['urgencia']:<10} {'[OK]' if ok_urg else '[DIF]'}")
        print(f"• Setor Roteado:         {triagem['setor_responsavel']:<15} | Esperado: {esperado['setor']:<15} {'[OK]' if ok_setor else '[DIF]'}")
        print(f"• Consulta BD (Pedido):  ID={banco['pedido_pesquisado']} | Localizado={banco['encontrado']} {'[OK]' if ok_banco else '[DIF]'}")
        print(f"• Resumo do Caso:        {triagem['resumo_problema']}")
        print(f"• Ação Recomendada:      {triagem['acao_recomendada']}")
        print(f"• Resposta ao Cliente:   \"{triagem['resposta_sugerida_cliente'][:120]}...\"")
        print(f"• Tempo de Execução:     {latencia_ms:.1f}ms")
        
        resultados_detalhados.append({
            "id": caso["id"],
            "titulo": caso["titulo"],
            "sentimento_ok": ok_sent,
            "urgencia_ok": ok_urg,
            "setor_ok": ok_setor,
            "banco_ok": ok_banco,
            "latencia_ms": latencia_ms
        })
        
    tempo_total = time.time() - inicio_geral
    
    # RELATÓRIO CONSOLIDADO E MÉTRICAS
    print("\n" + "=" * 80)
    print("                    RELATÓRIO CONSOLIDADO DE DESEMPENHO")
    print("=" * 80)
    print(f"Total de Cenários Avaliados:          {total_testes}")
    print(f"Acurácia de Classificação Sentimento: {(acertos_sentimento / total_testes) * 100:.1f}% ({acertos_sentimento}/{total_testes})")
    print(f"Acurácia de Classificação Urgência:   {(acertos_urgencia / total_testes) * 100:.1f}% ({acertos_urgencia}/{total_testes})")
    print(f"Acurácia de Roteamento de Setor:      {(acertos_setor / total_testes) * 100:.1f}% ({acertos_setor}/{total_testes})")
    print(f"Eficácia na Consulta ao Banco (SQL):  {(acertos_banco / total_testes) * 100:.1f}% ({acertos_banco}/{total_testes})")
    print(f"Tempo Total de Processamento:         {tempo_total:.2f}s (Média: {(tempo_total/total_testes)*1000:.1f}ms por chamado)")
    print("=" * 80)
    
    # Salva relatório em JSON para auditoria
    with open("resultado_testes.json", "w", encoding="utf-8") as f:
        json.dump({
            "metricas": {
                "total_testes": total_testes,
                "acuracia_sentimento_pct": (acertos_sentimento / total_testes) * 100,
                "acuracia_urgencia_pct": (acertos_urgencia / total_testes) * 100,
                "acuracia_setor_pct": (acertos_setor / total_testes) * 100,
                "eficacia_banco_pct": (acertos_banco / total_testes) * 100,
                "tempo_total_segundos": tempo_total
            },
            "detalhes": resultados_detalhados
        }, f, ensure_ascii=False, indent=2)
        
    print("\n[SUCESSO] Relatório de testes gravado no arquivo 'resultado_testes.json'.")


if __name__ == "__main__":
    executar_testes_e_analise()

