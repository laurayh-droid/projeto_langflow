# 🤖 Agente de Triagem e Roteamento de Chamados com Langflow & LangChain

Projeto desenvolvido para demonstrar a criação de um **Agente Inteligente de Triagem e Roteamento de Chamados de Suporte**, integrando o **Langflow** (orquestração visual) e os recursos fundamentais do ecossistema **LangChain** (Prompts, Modelos de Linguagem, Ferramentas/Tools e Saídas Estruturadas).

---

## 📌 1. Problema Real Solucionado

No dia a dia de centrais de atendimento ao cliente (Helpdesk, SAC e E-commerce), um dos maiores gargalos é o processo manual de triagem:
- **Sobrecarga de chamados:** Centenas de e-mails chegam sem classificação prévia.
- **Risco de insatisfação crítica:** Casos graves (ex: atrasos severos de entrega, retenções fiscais ou cobranças duplicadas) podem ficar parados na mesma fila de dúvidas simples.
- **Retrabalho de roteamento:** Chamados são frequentemente repassados entre setores (Financeiro, Logística, Técnico, Comercial) até encontrar o responsável correto.
- **Falta de dados contextuais:** O atendente precisa pesquisar manualmente o ID do pedido no banco de dados corporativo antes de poder redigir qualquer resposta.

### 💡 A Solução Implementada
O agente inteligente automatiza este fluxo de ponta a ponta:
1. **Lê o e-mail/ticket de suporte.**
2. **Detecta o sentimento** do cliente (`POSITIVO`, `NEUTRO` ou `NEGATIVO`).
3. **Avalia o nível de urgência** (`BAIXA`, `MEDIA`, `ALTA` ou `CRITICA`).
4. **Extrai o ID do pedido** e **executa uma consulta SQL** no banco de dados corporativo (`pedidos.db`), recuperando status, rastreio, previsão de entrega e notas fiscais.
5. **Roteia o chamado** para o setor responsável (`LOGISTICA`, `FINANCEIRO`, `SUPORTE_TECNICO` ou `COMERCIAL`).
6. **Gera um resumo executivo**, a **ação interna recomendada** e uma **minuta de resposta personalizada e empática** para envio imediato ao cliente.

---

## 🏗️ 2. Arquitetura da Solução e Recursos do Ecossistema LangChain

```
  ┌─────────────────┐       ┌───────────────────────┐       ┌────────────────────┐
  │ 1. Chat Input   │ ────> │ 2. Custom SQLite Tool │ ────> │ 3. Prompt Template │
  │ (Texto Ticket)  │       │ (Consulta pedidos.db) │       │ (Persona & Regras) │
  └─────────────────┘       └───────────────────────┘       └────────────────────┘
                                                                       │
                                                                       ▼
  ┌─────────────────┐       ┌───────────────────────┐       ┌────────────────────┐
  │ 5. Chat Output  │ <──── │  Output Parser / JSON │ <──── │ 4. LLM Model       │
  │ (Dossiê + Resp) │       │  (Contrato Pydantic)  │       │ (OpenAI/Groq/Mock) │
  └─────────────────┘       └───────────────────────┘       └────────────────────┘
```

### Componentes LangChain Utilizados:
- **`ChatPromptTemplate`:** Modela as diretrizes do especialista em suporte, definindo a separação entre contexto do cliente, dados recuperados do banco de dados e regras de negócio.
- **Modelos de Linguagem (`ChatOpenAI` / `ChatGroq`):** Executam a inferência semântica e raciocínio para a tomada de decisão.
- **`@tool` / Custom Component:** Conecta o agente ao banco SQLite corporativo, permitindo busca determinística de dados do pedido.
- **`PydanticOutputParser`:** Garante conformidade estrita da resposta nos formatos esperados (validação de tipos e Enums).
- **LCEL (LangChain Expression Language):** Encadeamento declarativo através de pipes (`prompt | llm | parser`).

---

## 📂 3. Estrutura de Arquivos do Projeto

```
trabalho_langflow/
│
├── fluxo_langflow_triagem.json     # Fluxo exportado pronto para importação no Langflow UI
├── langflow_component_custom.py    # Código do componente customizado Python para o Langflow
├── langchain_agent.py              # Implementação do Agente via LangChain (LCEL + Fallback)
├── database.py                     # Inicialização e consultas ao banco SQLite (pedidos.db)
├── test_agent.py                   # Bateria automatizada de testes práticos com 5 cenários
├── app_demo.py                     # Painel visual interativo completo em Streamlit
├── resultado_testes.json           # Relatório consolidado e métricas das avaliações
└── README.md                       # Documentação técnica do projeto
```

---

## 🚀 4. Como Executar e Demonstrar a Aplicação

### Opção A: Executar a Interface Web Interativa (Streamlit)
O projeto conta com um painel completo para demonstração em tempo real:
```bash
streamlit run app_demo.py
```
No painel você poderá:
- Testar chamados pré-cadastrados ou digitar mensagens livres.
- Visualizar os crachás de sentimento, urgência e setor roteado em tempo real.
- Inspecionar os registros do banco de dados SQLite.
- Executar a suíte de testes com 1 clique e conferir os gráficos de desempenho.

### Opção B: Executar os Testes Automatizados via Terminal
Para rodar a bateria de 5 cenários reais e gerar o relatório estatístico:
```bash
python test_agent.py
```

### Opção C: Importar e Executar no Langflow Visual
1. Inicie o Langflow no terminal:
   ```bash
   langflow run
   ```
2. Abra o navegador no endereço exibido (geralmente `http://localhost:7860`).
3. No painel inicial, clique em **"Import"** (ou arraste o arquivo).
4. Selecione o arquivo **`fluxo_langflow_triagem.json`**.
5. O fluxo será exibido no Canvas com todos os nós e conexões já configurados!
6. Clique no botão **"Playground"** para testar mensagens diretamente na interface visual.

---

## 📊 5. Resultados dos Testes Práticos

A bateria de testes avaliou 5 cenários reais complexos:
1. **Atraso Crítico em Entrega de Hardware (#10423):** Cliente furioso, pedido atrasado e retido em fiscalização interestadual.
2. **Cobrança Duplicada no Cartão de Crédito (PED-10890):** Duas cobranças de R$ 3.750,00 identificadas pelo gateway.
3. **Falha Técnica / Crash no Sistema (Sem Pedido):** Erro 500 no login do software corporativo.
4. **Cotação Comercial para Compra Corporativa em Lote:** Pedido de orçamento de 50 monitores com faturamento PJ.
5. **Elogio de Entrega com Solicitação de 2ª Via de NF (#10101):** Cliente satisfeito com a cadeira ergonômica pedindo a nota.

### Métricas de Desempenho Consolidadas:
| Métrica Avaliada | Acurácia Obtida | Amostra |
| :--- | :---: | :---: |
| **Classificação de Sentimento** | **100.0%** | 5/5 |
| **Classificação de Urgência** | **100.0%** | 5/5 |
| **Roteamento de Setor** | **100.0%** | 5/5 |
| **Consulta ao Banco de Dados (SQL)** | **100.0%** | 5/5 |
| **Latência Média por Chamado** | **~1.9 ms** | - |

