# 05 — Validação, benchmark e ablation

## Regra principal

Nenhum algoritmo entra no core apenas porque é conhecido, possui paper ou parece sofisticado.

Ele deve mostrar ganho.

## 1. Separação de dados

### Training
data/training/

Pode evoluir com novos dados rotulados.

### Benchmark
data/benchmark/

É holdout.

NÃO:
- treinar no benchmark;
- ajustar thresholds olhando gold;
- selecionar features com base nos erros do mesmo teste e depois reportar a mesma métrica como cega.

Se o benchmark for usado para desenvolvimento, ele deixa de ser holdout e deve ser substituído.

## 2. Splits necessários

### Group split
Usuário/accountId não pode aparecer simultaneamente em treino e teste.

### Temporal split
Quando houver histórico real:
- treinar em período anterior;
- validar em período posterior.

### Institution split
Quando houver volume:
- medir por banco/provedor.

### Segment split
Medir:
- PF;
- MEI;
- CNAE;
- faixas de histórico;
- faixa de volume financeiro.

## 3. Métricas de classificação

- accuracy;
- balanced accuracy;
- precision BUSINESS;
- recall BUSINESS;
- F1 BUSINESS;
- precision PERSONAL;
- recall PERSONAL;
- F1 PERSONAL;
- ROC-AUC;
- PR-AUC;
- confusion matrix.

## 4. Métricas do REVIEW

- coverage;
- reviewRate;
- autoDecisionAccuracy;
- errors_at_auto_decision;
- risk-coverage curve.

Objetivo:
aumentar automação sem esconder incerteza.

## 5. Calibração

- Brier Score;
- log loss;
- reliability diagram;
- ECE se implementado.

Avaliar antes e depois de Platt/isotonic.

## 6. Erro ponderado financeiramente

Problema:
errar R$ 10 e R$ 100.000 contam igualmente em accuracy.

Criar métricas auxiliares:

absolute_value_error_sum =
Σ |amount_i| para classificações erradas

weighted_error_rate =
Σ(|amount_i| × error_i) / Σ|amount_i|

Importante:
isso NÃO substitui métricas de classificação; é visão complementar de impacto.

Também separar:
- PERSONAL → BUSINESS;
- BUSINESS → PERSONAL;
- erro em receita;
- erro em transferência;
- erro em empréstimo.

## 7. Benchmark por dificuldade

Manter:
- EASY;
- MEDIUM;
- HARD;
- ADVERSARIAL.

Reportar cada grupo separadamente.

O objetivo não é inflar accuracy com casos óbvios.

## 8. Ablation tests

Para cada nova camada:

### Classificação
- Logistic baseline;
- CatBoost;
- Logistic + CatBoost ensemble;
- sem features históricas;
- com features históricas;
- sem CNAE;
- com CNAE.

### Behavioral
- sem anomaly features;
- + EWMA;
- + MAD;
- + CUSUM;
- + Page-Hinkley;
- + Isolation Forest quando aplicável.

### Capacity
Testar estabilidade/reprodutibilidade dos indicadores antes de qualquer uso em modelo de risco.

## 9. Critério de ganho

Um algoritmo pode ser aceito por três motivos:

1. melhora preditiva global;
2. melhora relevante em um subgrupo crítico;
3. adiciona função não coberta pelo baseline, como detecção de mudança ou explicabilidade.

Documentar sempre:
- baseline;
- variante;
- dataset;
- split;
- seed;
- métricas;
- intervalo de confiança quando possível;
- decisão KEEP / REJECT / EXPERIMENTAL.

## 10. Drift

### PSI

PSI = Σ (A_i - E_i) ln(A_i / E_i)

onde E = distribuição de desenvolvimento e A = distribuição atual.

Usar como indicador, não como prova estatística definitiva.

Monitorar:
- features;
- scores;
- taxa de REVIEW;
- categorias;
- bancos;
- CNAEs.

### KS / outras distâncias

Pode complementar PSI para comparar distribuições contínuas.

### Drift de performance

Quando existirem rótulos atrasados:
- acompanhar erro real ao longo do tempo;
- não depender apenas de drift de features.

## 11. Reprodutibilidade

Todo treino deve registrar:
- modelVersion;
- git SHA;
- dataset manifest;
- número de registros;
- grupos;
- seeds;
- parâmetros;
- dependências;
- métricas;
- data/hora;
- hash/identificador dos arquivos de treino.

## 12. Meta de dados

Etapas orientativas, não leis:
- POC séria: milhares de transações bem rotuladas e dezenas/centenas de contas;
- robustez maior: dezenas de milhares e diversidade de instituições/CNAEs;
- modelo de default: exige milhares de contratos com outcome de pagamento, incluindo quantidade suficiente de defaults.

Qualidade, diversidade e independência entre treino/teste são mais importantes que apenas volume bruto.
