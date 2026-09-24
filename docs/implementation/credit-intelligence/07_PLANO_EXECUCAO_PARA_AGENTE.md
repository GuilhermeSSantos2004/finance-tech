# 07 — Plano de execução para agente de implementação

Este arquivo deve ser usado como handoff para uma IA/Codex implementar a evolução do ScorByte.

## Regras obrigatórias

1. Ler README.md da raiz.
2. Ler docs/ALGORITMO.md.
3. Ler docs/CONTRATO_DADOS.md.
4. Ler docs/TESTES.md.
5. Ler todos os arquivos deste diretório.
6. Preservar o baseline atual.
7. Não mover data/benchmark para data/training.
8. Não usar gold do benchmark no treino/tuning.
9. Implementar incrementalmente.
10. Criar testes para cada etapa.
11. Não quebrar CLI existente sem camada de compatibilidade.
12. Não afirmar ganho sem benchmark.
13. Não implementar score de default sem outcomes reais de crédito.

## Estrutura de código sugerida

src/finance_classifier/
- existing files...
- models/
  - logistic_baseline.py
  - catboost_challenger.py
  - calibration.py
  - ensemble.py
- semantics/
  - taxonomy.py
  - classifier.py
  - relationships.py
- behavior/
  - ewma.py
  - robust_stats.py
  - cusum.py
  - change_detection.py
  - seasonality.py
  - isolation.py
- capacity/
  - revenue.py
  - concentration.py
  - cashflow.py
  - debt_service.py
  - stability.py
- evaluation/
  - metrics.py
  - calibration.py
  - ablation.py
  - drift.py
- explain/
  - model_explainer.py
- schemas/
  - outputs.py

A estrutura pode ser ajustada se o código atual recomendar outra organização.

## FASE 0 — Congelar baseline

Entregáveis:
- rodar testes atuais;
- registrar métricas baseline;
- salvar manifest do dataset;
- registrar git SHA;
- confirmar benchmark separado;
- não alterar comportamento do baseline.

Acceptance:
- testes existentes passam;
- relatório baseline reproduzível.

## FASE 1 — Contrato de Financial Semantics

Adicionar target/saída secundária sem quebrar BUSINESS/PERSONAL.

Taxonomia inicial:
REVENUE, EXPENSE, TRANSFER, INTERNAL_TRANSFER, DEBT, LOAN, REFUND, TAX, SUPPLIER, LABOR, INVESTMENT, OTHER.

Entregáveis:
- schema;
- validação;
- documentação;
- testes;
- possibilidade de UNKNOWN/REVIEW semântico.

Não inventar labels nos dados atuais.

## FASE 2 — Relationship Engine

Implementar primeiro regras testáveis:

### Transferência própria candidata
Sinais:
- mesma titularidade quando disponível de forma segura;
- valores iguais/próximos;
- timestamps próximos;
- crédito e débito em contas diferentes;
- identificadores correlacionáveis quando fornecidos.

### Refund/reversal candidate
- valores iguais/próximos;
- sinais opostos;
- janela temporal;
- merchant/contraparte compatível.

Entregáveis:
- relationship features;
- confidence;
- reason codes;
- testes adversariais.

Nunca apagar transações. Criar relações.

## FASE 3 — CatBoost challenger

Adicionar dependência de maneira opcional se possível.

Entradas:
- features estruturadas atuais;
- categóricas;
- representações textuais escolhidas;
- features históricas somente se calculadas sem leakage.

Executar:
- group split;
- mesmos folds do baseline;
- tabela comparativa.

Acceptance:
- não substituir baseline automaticamente;
- gerar model card separado;
- decisão KEEP/REJECT/EXPERIMENTAL.

## FASE 4 — Calibration + REVIEW

Implementar:
- Platt scaling;
- isotonic se quantidade de validação suportar;
- Brier;
- reliability curve;
- coverage;
- reviewRate;
- autoDecisionAccuracy.

Thresholds devem ser escolhidos em validação.

O benchmark final continua cego.

## FASE 5 — Behavioral Engine v1

Implementar funções puras com testes:

1. EWMA;
2. variance/standard deviation exponencial se necessário;
3. MAD;
4. modified z-score;
5. CUSUM.

Cada função recebe série ordenada e retorna estado/features.

Não acoplar diretamente à decisão de crédito.

Testar:
- série estável;
- spike;
- drop;
- deterioração gradual;
- outlier extremo;
- pouco histórico.

## FASE 6 — Change Detection + Seasonality

Implementar/avaliar:
- Page-Hinkley;
- STL somente com histórico suficiente.

Definir minimum_history por frequência.

Saída deve incluir insufficient_history.

## FASE 7 — Capacity Metrics v1

Implementar:
- verified revenue aggregation;
- monthly median;
- P25;
- CV;
- HHI;
- top1/top3 payer share;
- recurring revenue ratio;
- operating cash flow;
- available cash flow;
- dscr_proxy;
- trends.

Criar testes numéricos determinísticos.

## FASE 8 — Explainability

Logistic:
- top coefficient contributions.

CatBoost:
- SHAP somente se modelo CatBoost for mantido.

Gerar reason codes de alto nível, por exemplo:
- HIGH_REVENUE_CONCENTRATION;
- REVENUE_DECLINE;
- HIGH_VOLATILITY;
- POSITIVE_FREE_CASH_FLOW;
- INSUFFICIENT_HISTORY;
- MODEL_DISAGREEMENT.

## FASE 9 — Isolation Forest

Só iniciar quando houver volume/history.

Input:
features mensais/por janela, não texto bruto.

Comparar:
- behavioral engine sem Isolation Forest;
- + Isolation Forest.

Manter se detectar casos adicionais úteis com taxa de falso positivo aceitável.

## FASE 10 — Drift e observabilidade

Implementar:
- PSI;
- distribuição de scores;
- review rate;
- feature missingness;
- métricas por CNAE/banco;
- performance quando labels chegarem.

## FASE 11 — API

Somente após estabilizar contratos internos.

Endpoints sugeridos:
- POST /v1/transactions/classify
- POST /v1/financial-profile/analyze
- GET /v1/models/{version}
- GET /v1/analyses/{id}

Não implementar decisões de aprovação/reprovação como verdade do modelo atual.

## FASE 12 — Security hardening

Antes de integração financeira real:
- autenticação;
- autorização;
- tenant isolation;
- secrets;
- encryption;
- audit;
- rate limiting;
- schema validation;
- consent context;
- retention.

Para integração Open Finance, validar especificação FAPI-BR vigente no momento da implementação.

## Testes mínimos

### Unit
- fórmulas;
- edge cases;
- missing values;
- zero division;
- small history.

### Integration
- transaction → semantics → behavior → capacity.

### Leakage
- target não entra;
- accountId não entra;
- dados futuros não entram em features históricas;
- benchmark não entra em treino.

### Regression
- baseline v0.1.0 continua reproduzível.

## Definition of Done de cada algoritmo

Um algoritmo só é “implementado” quando existir:
- código;
- teste;
- documentação;
- parâmetros versionados;
- output schema;
- benchmark;
- ablation;
- decisão KEEP/REJECT/EXPERIMENTAL.

## Prioridade recomendada

P0:
- semântica financeira;
- relationship engine;
- CatBoost challenger;
- calibration;
- EWMA;
- MAD;
- CUSUM;
- HHI;
- CV;
- verified/sustainable revenue components;
- cash flow;
- dscr_proxy;
- benchmark/ablation.

P1:
- Page-Hinkley;
- STL;
- SHAP;
- drift;
- reason codes.

P2:
- Isolation Forest;
- ensembles mais complexos;
- otimizações avançadas.

## Restrição crítica sobre “usar todos”

Este blueprint contém todos os algoritmos considerados úteis, mas isso NÃO significa ativar todos em produção.

A implementação deve permitir testar todos. A produção mantém apenas os que:
- melhorarem resultado;
- adicionarem função complementar;
- forem auditáveis;
- tiverem custo/latência aceitáveis.

Esse princípio evita complexidade sem ganho.
