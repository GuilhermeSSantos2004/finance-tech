# 02 — Transaction Intelligence

## Objetivo

Aumentar a precisão e a robustez da classificação de transações sem abandonar o baseline atual.

## A. Baseline — TF-IDF + Logistic Regression

Status: existente.

### TF-IDF

Representação simplificada:

TFIDF(t,d) = TF(t,d) × log(N / DF(t))

Character n-grams são adequados para textos bancários ruidosos, abreviados e truncados.

Exemplos:
- PIXREC;
- RSCSS;
- nomes cortados;
- códigos misturados.

### Regressão Logística

Probabilidade binária:

p(y=1|x) = 1 / (1 + exp(-(β0 + βᵀx)))

Vantagens:
- simples;
- reproduzível;
- probabilística;
- interpretável;
- bom baseline para pouco dado.

Não remover sem evidência.

## B. Challenger — CatBoost

Status: planejado.

### Por que testar

O domínio mistura:
- variáveis categóricas;
- numéricas;
- contexto de CNAE;
- banco;
- operationType;
- paymentMethod;
- categoria;
- contraparte;
- histórico;
- texto/representações derivadas.

CatBoost usa gradient boosting e possui tratamento próprio de variáveis categóricas com ordered statistics/ordered boosting.

Forma conceitual de boosting:

F_M(x) = F_0(x) + η Σ_m f_m(x)

onde f_m é uma árvore adicionada sequencialmente.

### Não fazer

- não substituir Logistic apenas porque CatBoost é mais complexo;
- não usar o benchmark cego para tuning;
- não colocar CPF/CNPJ completo como feature;
- não usar accountId como feature;
- não usar target ou campos derivados do target.

### Critério de aceite

CatBoost entra se:
- melhorar métricas de classificação no holdout de usuários não vistos; OU
- mantiver qualidade semelhante com ganho relevante em um subgrupo importante;
- não piorar materialmente calibração;
- não aumentar de forma inaceitável o custo/latência.

## C. Ensemble

Status: opcional.

Somente implementar se Logistic e CatBoost cometerem erros complementares.

Exemplo simples:

p_ensemble = w × p_logistic + (1-w) × p_catboost

O peso w deve ser aprendido/selecionado apenas em validação, nunca no teste cego.

Também testar regras de discordância:
- ambos concordam e estão calibrados → decisão automática;
- modelos divergem fortemente → REVIEW;
- caso fora da distribuição → REVIEW.

## D. Probability Calibration

Objetivo: fazer a confiança prevista se aproximar da frequência empírica observada.

### Platt scaling

p_cal = 1 / (1 + exp(Af + B))

onde f é o score do classificador e A/B são ajustados em dados de calibração.

### Isotonic Regression

Alternativa não paramétrica monotônica, mais flexível, mas exige mais dados.

### Métricas

- Brier Score;
- calibration curve/reliability diagram;
- Expected Calibration Error, se implementado;
- log loss.

Não interpretar 0.90 como “90% de chance real” antes da calibração ser validada.

## E. Selective Classification / REVIEW

REVIEW deve ser tratado como capacidade do sistema de se abster quando há incerteza.

A decisão deve futuramente considerar mais que um threshold fixo:
- confiança calibrada;
- discordância entre modelos;
- dados faltantes;
- out-of-distribution;
- regras de segurança financeira.

Métricas:
- coverage = decisões automáticas / total;
- reviewRate = REVIEW / total;
- autoDecisionAccuracy = acurácia apenas nas decisões automáticas;
- risk-coverage curve.

## F. Segundo nível — natureza financeira

Criar target separado de BUSINESS/PERSONAL.

Classes iniciais:
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

Evitar forçar uma única taxonomia se dados reais mostrarem sobreposição. Pode ser necessário modelo hierárquico ou multi-label.

## G. Relationship features

Features candidatas:
- same_owner_transfer_candidate;
- reversal_candidate;
- days_since_matching_debit;
- amount_match_ratio;
- counterparty_frequency_30d/90d/180d;
- counterparty_credit_ratio;
- counterparty_debit_ratio;
- recurring_amount_cv;
- months_active;
- days_since_first_seen;
- same_amount_count;
- provider/bank;
- transaction channel.

## H. Explicabilidade

Logistic:
- coeficientes por feature;
- top contribuições textuais e estruturadas.

CatBoost:
- SHAP/TreeSHAP;
- explicação por previsão;
- agregação por feature group.

Nunca mostrar ao usuário apenas um score sem fatores que o sustentam.
