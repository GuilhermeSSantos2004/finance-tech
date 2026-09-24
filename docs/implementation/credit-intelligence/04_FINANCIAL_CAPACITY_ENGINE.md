# 04 — Financial Capacity Engine

## Objetivo

Transformar transações classificadas em indicadores financeiros compreensíveis.

Esta camada NÃO deve, neste momento, emitir uma probabilidade de default.

## A. Receita verificada

Antes de medir capacidade, separar entrada bancária de receita.

Não contam automaticamente como receita:
- transferência própria;
- empréstimo;
- estorno;
- reembolso;
- aporte;
- venda eventual de ativo;
- transferência familiar.

Resultado:

verified_business_inflow = soma das entradas classificadas como receita empresarial com critérios de confiança definidos.

Sempre expor:
- valor;
- cobertura de classificação;
- percentual em REVIEW;
- quantidade de meses observados.

## B. Receita sustentável — métrica ScorByte

Importante:
“Receita sustentável ScorByte” é uma métrica de engenharia a ser validada. Não é um padrão regulatório nem uma fórmula acadêmica única.

### Versão inicial recomendada

Não criar score arbitrário de 0–100.

Calcular primeiro componentes independentes:

1. monthly_verified_revenue;
2. median_verified_revenue;
3. P25_verified_revenue;
4. revenue_cv;
5. recurring_revenue_ratio;
6. customer_hhi;
7. trend_90d/180d;
8. history_months;
9. data_coverage.

Primeira estimativa conservadora possível:

sustainable_revenue_v0 = mediana ou P25 das receitas mensais verificadas em janela definida.

A escolha mediana vs P25 deve ser validada contra um objetivo real. Sem outcomes de crédito, apresentar como estimativa de estabilidade/recorrência, não como “limite de crédito ideal”.

## C. Coeficiente de Variação

CV = σ / μ

Para μ > 0.

Uso:
comparar estabilidade relativa de séries com escalas diferentes.

Cuidados:
- instável quando média ≈ 0;
- sensível a outliers;
- usar junto com MAD/IQR;
- não transformar diretamente em decisão de crédito.

## D. HHI adaptado para concentração de clientes

Fórmula:

HHI = Σ s_i²

onde s_i é a participação do cliente/pagador i na receita total da janela.

Se shares estiverem entre 0 e 1:
- próximo de 1 → concentração alta;
- menor → receita distribuída.

Exemplo:
90% + 10%:
HHI = 0.9² + 0.1² = 0.82

10 clientes com 10%:
HHI = 10 × 0.1² = 0.10

### Atenção

HHI é um índice clássico de concentração usado em economia/antitruste. No ScorByte estamos reutilizando a matemática para concentração de receita por cliente.

NÃO reutilizar automaticamente os thresholds antitruste do DOJ como thresholds de risco financeiro.

Calibrar thresholds com dados de pequenos negócios/outcomes.

Também expor:
- top1_share;
- top3_share;
- active_payers;
- payer_churn.

## E. Free Cash Flow operacional simplificado

Primeiro estágio de engenharia:

operating_cash_flow =
verified_operating_inflows
- verified_operating_outflows
- taxes
- recurring_operating_obligations

Depois:

available_cash_flow =
operating_cash_flow
- identified_personal_commitments aplicáveis ao contexto analisado
- existing_debt_service

Definições devem ser versionadas. Não misturar conceitos contábeis formais sem documentação.

## F. DSCR adaptado

Referência geral:

DSCR = cash flow available for debt service / debt service

Para o ScorByte, definir explicitamente o numerador.

Exemplo de feature:

capacity.dscr_proxy =
cash_flow_available_for_debt_service
/
existing_monthly_debt_service

Se debt_service = 0:
- não retornar infinito;
- retornar indicador debt_service_zero e DSCR null/NA ou convenção documentada.

### Atenção

O DSCR usado em diferentes linhas de crédito pode ter definições distintas. O ScorByte deve chamar a primeira versão de dscr_proxy ou dscr_estimate até validar a definição com parceiro financeiro.

## G. Tendência

Calcular por janelas:
- 30d;
- 90d;
- 180d;
- 365d.

Possíveis métodos:
- variação percentual simples;
- regressão linear robusta;
- slope da série dessazonalizada;
- comparação rolling median.

Evitar definir tendência por dois pontos isolados.

## H. Recorrência de receita

Features:
- payer_frequency;
- months_with_payment;
- regularity;
- amount_cv_by_payer;
- recurring_income_share;
- recurring_payers_count.

Recorrência não garante receita futura, apenas descreve o histórico.

## I. Concentração e dependência

Além do HHI:
- share do maior pagador;
- share dos 3 maiores;
- diversidade de pagadores;
- churn;
- tempo de relacionamento.

## J. Saída sugerida da camada

capacity.verified_revenue_30d
capacity.verified_revenue_90d
capacity.median_monthly_revenue
capacity.p25_monthly_revenue
capacity.revenue_cv
capacity.customer_hhi
capacity.top1_customer_share
capacity.top3_customer_share
capacity.recurring_revenue_ratio
capacity.operating_cash_flow
capacity.available_cash_flow
capacity.dscr_proxy
capacity.revenue_trend_90d
capacity.revenue_trend_180d
capacity.history_months
capacity.data_coverage

## K. O que mostrar no produto

Em vez de apenas score:

- entradas observadas;
- receita identificada;
- transferências próprias excluídas;
- empréstimos identificados;
- receita mensal mediana;
- estabilidade;
- concentração;
- fluxo disponível;
- dívida observada;
- fatores positivos;
- fatores de atenção;
- cobertura dos dados.

Isso responde melhor à pergunta “como o MEI se beneficia?” e melhora a explicabilidade para a instituição.
