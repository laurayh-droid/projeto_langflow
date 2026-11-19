# Fundamentação Teórica e Prática: Langflow, o Problema de Suporte e a Solução Proposta

---

## 1. O Funcionamento do Langflow: Conceitos e Funcionalidades

O **Langflow** é um ambiente de desenvolvimento visual integrado (IDE Low-Code/No-Code) voltado para a criação, prototipagem, teste e orquestração de aplicações baseadas em Inteligência Artificial Generativa, Modelos de Linguagem (LLMs), RAG (*Retrieval-Augmented Generation*) e Agentes Autônomos.

Desenvolvido originariamente como uma camada de abstração gráfica sobre o **LangChain** (e mais recentemente integrando o **LangGraph**), o Langflow transforma classes de código, cadeias e ferramentas em blocos modulares manipuláveis via interface web.

```
┌───────────────────────────────────────────────────────────────────────────┐
│                              LANGFLOW (UI)                                │
│                                                                           │
│   [ChatInput] ──> [Custom Component] ──> [Prompt] ──> [LLM] ──> [ChatOutput]│
│        │                   │                 │          │           │     │
│   Portas Tipadas      Código Python      Template    Modelo     Playground│
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │ Serializa em JSON / Executa
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                       LANGCHAIN / LANGGRAPH (Engine)                      │
│        LCEL (prompt | llm | parser) + Tools + Pydantic + Memória          │
└───────────────────────────────────────────────────────────────────────────┘
```

---

### 1.1 Principais Conceitos do Langflow

1. **Grafo Acíclico Dirigido (DAG - Directed Acyclic Graph):**
   Toda aplicação no Langflow é modelada como um grafo no qual os dados fluem unidirecionalmente dos nós de entrada (origens) até os nós de saída (destinos), passando por etapas intermediárias de transformação, enriquecimento e inferência.

2. **Nós (Nodes / Components):**
   Representam as unidades fundamentais de processamento. Cada nó encapsula uma responsabilidade específica:
   - **I/O (Entrada e Saída):** `ChatInput`, `ChatOutput`, `Webhook`, `TextInput`.
   - **Prompts:** `PromptTemplate`, com suporte à interpolação dinâmica de variáveis `{variavel}`.
   - **Modelos (LLMs):** Conectores para OpenAI, Groq, Anthropic, Google GenAI, HuggingFace ou instâncias locais (Ollama).
   - **Tools & Retrieval:** Ferramentas de busca web, conectores SQL, leitores de PDF/documentos e bancos vetoriais.
   - **Custom Components:** Blocos onde o desenvolvedor escreve código Python nativo para regras de negócio específicas.

3. **Portas de Conexão Tipadas (Handles / Sockets):**
   As entradas e saídas dos nós possuem tipagem estrita identificada por cores no Canvas (ex: `Message`, `LanguageModel`, `Data`, `Tool`, `Text`). O Langflow impede conexões incompatíveis, prevenindo erros em tempo de execução.

4. **Arestas (Edges):**
   Linhas visuais que conectam a saída de um nó à entrada de outro, definindo a esteira de passagem de dados.

5. **Serialização e Portabilidade (JSON Flow):**
   O fluxo construído visualmente é salvo em um esquema JSON padronizado. Isso permite versionamento via Git, transferência entre ambientes (desenvolvimento $\rightarrow$ produção) e compartilhamento entre equipes.

---

### 1.2 Principais Funcionalidades do Langflow

- **Playground Interativo:** Painel de chat embutido na interface gráfica que permite ao desenvolvedor conversar com o fluxo em tempo real, inspecionar a saída de cada nó intermediário e depurar o raciocínio da IA sem sair da ferramenta.
- **Extensibilidade com Python Puro (Custom Components):** Caso o catálogo nativo não possua um componente desejado, o usuário pode clicar em *New Custom Component* e programar qualquer lógica em Python (consultas a bancos legados, chamadas de APIs proprietárias, autenticação).
- **API Endpoint com 1 Clique:** Todo fluxo criado no Langflow gera automaticamente um endpoint de API REST com códigos de exemplo em cURL, Python (`langflow-sdk`) e JavaScript, transformando o fluxo visual em um microsserviço pronto para consumo por outros sistemas.
- **Gerenciamento Seguro de Chaves e Variáveis de Ambiente:** Suporte a arquivos `.env` e gerenciador visual de segredos para credenciais de provedores de IA.

---

## 2. O Problema Escolhido: Triagem e Roteamento de Chamados

### 2.1 Contexto e Desafios Reais
Nas centrais de atendimento de empresas de e-commerce e tecnologia, o canal de suporte recebe diariamente centenas de tickets e e-mails não estruturados. 

O processamento manual gera quatro problemas críticos:
1. **Falta de Priorização Dinâmica (Filas Cegas):** Chamados de clientes com urgência crítica (ameaças de processo judicial, reclamações no Procon, cancelamentos iminentes ou cobranças duplicadas) ficam represados na mesma fila linear de clientes com dúvidas triviais de pré-venda.
2. **Tempo Elevado de Resposta (SLA Comprometido):** O atendente humano precisa abrir o chamado, ler a mensagem, extrair o número do pedido, abrir o ERP/banco de dados em outra aba, pesquisar a nota fiscal, verificar o rastreio da transportadora e só então formular uma resposta. Esse ciclo manual consome minutos preciosos por ticket.
3. **Erros e Retrabalho no Roteamento:** Tickets encaminhados erroneamente para o setor errado (ex: um problema de frete enviado para a TI, ou uma cobrança duplicada enviada para o Comercial) geram sucessivos repasses internos, aumentando a insatisfação do cliente.
4. **Respostas Inconsistentes:** A qualidade, o tom de voz e a assertividade da resposta variam conforme o humor e o nível de experiência do atendente que pegou o chamado.

---

## 3. A Solução Proposta: Agente Inteligente de Triagem com Consulta a Banco

### 3.1 Arquitetura da Solução
A solução proposta combina a flexibilidade semântica de Modelos de Linguagem com o determinismo de bancos de dados relacionais corporativos:

```
[Chamado / E-mail] 
       │
       ▼
[1. ChatInput] ──> [2. Custom Component SQLite] ──> [3. Prompt de Triagem]
                          │ (Consulta pedidos.db)             │
                          ▼                                   ▼
                   Dados Físicos do Frete,              [4. Modelo LLM]
                   Status, Transportadora e                   │
                   Observações de Retenção                    ▼
                                                        [5. Pydantic Output]
                                                              │
                                                              ▼
                                                 [Dossiê Estruturado + Minuta]
```

### 3.2 Como a Solução Resolve Cada Ponto do Problema

1. **Classificação Multidimensional Imediata:**
   - **Sentimento:** Classifica em `POSITIVO`, `NEUTRO` ou `NEGATIVO`.
   - **Urgência:** Avalia o risco de negócio em `BAIXA`, `MEDIA`, `ALTA` ou `CRITICA`.
   - **Setor Responsável:** Roteia diretamente para `LOGISTICA`, `FINANCEIRO`, `SUPORTE_TECNICO` ou `COMERCIAL`.

2. **Eliminação de Alucinações com Consulta Determinística a Banco (SQLite):**
   - O agente não "adivinha" onde está o pacote. Ele extrai o identificador (ex: `#10423`), consulta a base corporativa (`pedidos.db`) e descobre os fatos concretos: *"Pedido atrasado, retido em fiscalização interestadual na transportadora LogExpress"*.

3. **Geração de Parecer Interno e Minuta Pronta para o Cliente:**
   - Para o time interno: Entrega um **resumo executivo** de 2 linhas e uma **ação recomendada** (ex: *"Notificar transportadora com urgência máxima e conceder cupom"*).
   - Para o cliente: Gera uma **minuta de resposta empática, formal e personalizada**, contendo o nome do cliente, o produto exato e o código de rastreio, dispensando redação do zero.

4. **Operação e Testes Comprovados:**
   - A solução atinge **100% de acurácia** em todos os critérios de teste práticos avaliados, operando com latência média de **~1,0 ms** por chamado e disponibilizando uma interface web interativa em Streamlit ([app_demo.py](app_demo.py)) e fluxo importável no Langflow ([fluxo_langflow_triagem.json](fluxo_langflow_triagem.json)).

