# 03 — Behavioral / Anomaly Engine

## Objetivo

Responder:

“Esta movimentação ou este período está coerente com o comportamento histórico do usuário/MEI?”

Essa camada não substitui o classificador. Ela gera features comportamentais.

## Origem da ideia

Foi analisada uma implementação existente de monitoramento de séries que utiliza:
- baseline por slot temporal;
- média e variância exponenciais;
- bandas por sigma;
- exclusão de outliers do baseline.

O conceito é útil para finanças, mas os parâmetros de monitoramento técnico NÃO devem ser copiados diretamente. Finanças possuem sazonalidade, frequência e distribuição diferentes.

## A. EWMA / EMA

### Fórmula

EWMA_t = λY_t + (1-λ)EWMA_(t-1)

0 < λ ≤ 1.

λ alto:
- reage rápido;
- esquece histórico mais rápido.

λ baixo:
- preserva memória;
- reage mais lentamente.

No domínio financeiro, λ deve ser escolhido por backtest por tipo de série.

Séries candidatas:
- verified_revenue;
- operating_expense;
- free_cash_flow;
- balance;
- debt_service;
- number_of_clients;
- average_ticket.

### Saídas

- ewma_value;
- deviation_from_ewma;
- normalized_deviation;
- direction;
- persistence.

## B. Bandas estatísticas / sigma

Forma simples:

upper = μ + kσ
lower = μ - kσ

Útil como sinal, mas não assumir normalidade sem validação.

Em valores financeiros com caudas longas, combinar com métodos robustos.

## C. Median + MAD

### Fórmula

MAD = median(|x_i - median(x)|)

Modified Z-score:

M_i = 0.6745 × (x_i - median(x)) / MAD

Vantagem:
- média e desvio padrão são sensíveis a valores extremos;
- mediana/MAD são muito mais robustos.

Uso:
- entrada muito alta;
- despesa extraordinária;
- salto de saldo;
- mudança de ticket;
- receita fora do comportamento.

Saídas:
- robust_location;
- mad;
- modified_z;
- robust_anomaly_flag.

Nunca eliminar automaticamente o ponto. Marcar, explicar e decidir se ele deve ou não atualizar o baseline.

## D. Outlier exclusion do baseline

Problema:
uma venda extraordinária, empréstimo ou venda de ativo pode mudar artificialmente o “normal”.

Estratégia:
- detectar outlier;
- registrar o evento;
- permitir classificação semântica;
- decidir se o ponto entra no baseline da métrica.

Exemplo:
entrada de empréstimo deve existir no histórico, mas não deve aumentar o baseline de receita operacional.

## E. CUSUM

Objetivo:
detectar pequenos desvios persistentes.

Forma padronizada:

C⁺_t = max(0, C⁺_(t-1) + z_t - k)
C⁻_t = max(0, C⁻_(t-1) - z_t - k)

Alerta quando C⁺ ou C⁻ ultrapassa h.

k = allowance/reference value.
h = decision threshold.

Aplicações:
- queda gradual de receita;
- crescimento gradual de despesas;
- crescimento de dívida;
- redução de saldo;
- deterioração de free cash flow.

k e h devem ser calibrados em backtest, não fixados por intuição.

## F. Page-Hinkley

Objetivo:
detectar mudança estrutural/regime.

Forma conceitual:

m_t = Σ(x_t - média_t - δ)
M_t = min(m_1 ... m_t)
PH_t = m_t - M_t

Sinaliza mudança quando PH_t > λ_threshold.

Uso:
- negócio mudou de patamar;
- faturamento estabilizou em nível muito menor;
- comportamento financeiro mudou e o baseline antigo não representa mais o cliente.

Não confundir:
- anomalia pontual;
- tendência persistente;
- mudança de regime.

São fenômenos diferentes.

## G. STL — tendência e sazonalidade

Quando houver histórico suficiente e frequência regular:

Y_t = Trend_t + Seasonal_t + Remainder_t

STL usa LOESS para decompor série.

Aplicações:
- negócios sazonais;
- comparação dezembro vs dezembro em vez de dezembro vs novembro;
- distinguir queda real de padrão sazonal esperado.

Pré-condição:
histórico suficiente. Não usar STL em 2–3 meses e fingir que existe sazonalidade aprendida.

## H. Isolation Forest

Fase posterior.

Objetivo:
anomalia multivariada.

Vetor de exemplo por mês:
- revenue;
- expenses;
- free_cash_flow;
- HHI;
- CV;
- debt_service;
- balance;
- client_count;
- avg_ticket;
- pix_in;
- pix_out.

Isolation Forest isola observações por partições aleatórias; pontos anômalos tendem a exigir caminhos menores.

Score clássico:

s(x,n) = 2^(-E[h(x)] / c(n))

Uso:
complementar, não substituir detecção interpretável.

Critério:
somente entrar se acrescentar detecção útil em ablation e se for possível explicar as features que motivaram a anomalia.

## I. Slots temporais financeiros

Não copiar slots de infraestrutura do tipo “segunda 08:30”.

Testar granularidades compatíveis com finanças:
- dia da semana;
- dia do mês;
- semana do mês;
- mês;
- dias próximos a vencimentos;
- janelas 7/30/90/180/365 dias.

## J. Features finais desta camada

behavior.revenue_ewma_delta
behavior.revenue_modified_z
behavior.expense_modified_z
behavior.revenue_cusum_down
behavior.expense_cusum_up
behavior.regime_change_score
behavior.seasonal_residual
behavior.multivariate_anomaly_score
behavior.baseline_history_count
behavior.insufficient_history

Cada feature deve guardar:
- versão do algoritmo;
- janela;
- parâmetros;
- timestamp de cálculo.
