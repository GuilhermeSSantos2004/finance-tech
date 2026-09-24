# 01 — Arquitetura e estado atual

## Estado confirmado do repositório

A versão atual usa:

- TF-IDF de character n-grams 3–5;
- features estruturadas com DictVectorizer;
- FeatureUnion;
- LogisticRegression com class_weight=balanced;
- target BUSINESS/PERSONAL;
- REVIEW como decisão operacional;
- GroupShuffleSplit por accountId;
- dataset inicial sintético e pequeno.

O baseline deve ser preservado. Ele é importante para provar se modelos mais complexos realmente geram ganho.

## Problema técnico real

Uma transação isolada não contém toda a informação necessária.

Exemplos:
- PIX de CPF pode ser receita empresarial;
- pagamento para CNPJ pode ser consumo pessoal;
- transferência própria pode parecer receita/despesa;
- empréstimo recebido pode parecer faturamento;
- estorno pode parecer receita;
- compra de combustível pode ser pessoal ou operacional.

Logo, a arquitetura precisa separar perguntas diferentes.

## Arquitetura alvo

Open Finance / dados bancários
→ Normalização e Data Quality
→ Transaction Intelligence
→ Financial Semantics
→ Relationship Engine
→ Behavioral Intelligence
→ Financial Capacity Engine
→ Explainability / Audit
→ API B2B para banco/fintech

## Camada 1 — Transaction Intelligence

Pergunta:
“Qual é o contexto provável desta transação?”

Saída:
- BUSINESS;
- PERSONAL;
- REVIEW.

Modelos:
- Logistic Regression baseline;
- CatBoost challenger;
- eventual ensemble validado.

## Camada 2 — Financial Semantics

Pergunta:
“Qual foi a natureza econômica da movimentação?”

Saída inicial:
- REVENUE;
- EXPENSE;
- TRANSFER;
- INTERNAL_TRANSFER;
- DEBT;
- LOAN;
- REFUND;
- TAX;
- SUPPLIER;
- LABOR;
- INVESTMENT;
- OTHER.

O segundo nível é necessário porque BUSINESS não significa receita e PERSONAL não significa despesa.

## Camada 3 — Relationship Engine

Relaciona eventos que não devem ser analisados separadamente.

Casos:
- transferência entre contas do mesmo titular;
- compra ↔ estorno;
- parcela ↔ compra original;
- empréstimo ↔ parcelas;
- receita recorrente ↔ mesma contraparte;
- múltiplos lançamentos do mesmo evento.

Essa camada deve começar determinística/heurística e depois gerar features para ML.

## Camada 4 — Behavioral Intelligence

Pergunta:
“Isso é normal para este usuário/MEI?”

Sinais:
- receita abaixo do padrão;
- gasto acima do padrão;
- crescimento de dívida;
- queda gradual;
- mudança estrutural de comportamento;
- mês fora da distribuição histórica.

Métodos:
- EWMA;
- MAD;
- CUSUM;
- Page-Hinkley;
- STL;
- Isolation Forest em fase posterior.

## Camada 5 — Financial Capacity

Pergunta:
“O que o histórico indica sobre a capacidade financeira?”

Indicadores:
- receita verificada;
- receita sustentável;
- free cash flow;
- DSCR;
- HHI de concentração de clientes;
- volatilidade;
- tendência;
- recorrência;
- concentração de receita;
- compromissos financeiros.

## O que NÃO afirmar

Até existirem dados de crédito pós-concessão, não afirmar que o sistema calcula:
- probabilidade real de default;
- score bancário validado;
- aprovação/reprovação ótima de crédito;
- expected loss;
- LGD/EAD.

BUSINESS/PERSONAL e capacidade financeira são inputs potenciais para crédito, não equivalem a um modelo de risco.

## Princípio de implementação

Cada camada deve produzir features versionadas. Exemplo:

transaction.*
semantic.*
relationship.*
behavior.*
capacity.*

Isso permite:
- auditar a origem de cada variável;
- executar ablation tests;
- trocar um algoritmo sem quebrar as demais camadas;
- explicar a decisão final.
