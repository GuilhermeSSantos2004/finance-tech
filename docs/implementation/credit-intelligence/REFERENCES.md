# Referências técnicas e fontes

As referências abaixo sustentam os métodos. A adaptação ao ScorByte deve ser validada empiricamente.

## Classificação e boosting

### CatBoost
Prokhorenkova, L. et al. CatBoost: unbiased boosting with categorical features. NeurIPS 2018.
https://proceedings.neurips.cc/paper/2018/hash/14491b756b3a51daac41c24863285549-Abstract.html

Uso no ScorByte:
challenger para features categóricas + estruturadas.

## Probability calibration

Niculescu-Mizil, A.; Caruana, R. Predicting Good Probabilities with Supervised Learning. ICML 2005.
https://doi.org/10.1145/1102351.1102430

Uso:
validar Platt scaling/isotonic e evitar interpretar score cru como probabilidade real.

## Reject option / selective classification

Chow, C. K. On optimum recognition error and reject tradeoff. IEEE Transactions on Information Theory, 1970.
https://doi.org/10.1109/TIT.1970.1054406

Uso:
fundamentação do trade-off erro vs rejeição; REVIEW deve ser medido por coverage e risco.

## Explainability

Lundberg, S.; Lee, S. A Unified Approach to Interpreting Model Predictions. NeurIPS 2017.
https://papers.neurips.cc/paper_files/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html

Uso:
SHAP para explicar CatBoost e contribuições por feature.

## Anomalias e monitoramento

### EWMA
NIST/SEMATECH Engineering Statistics Handbook — EWMA Control Charts.
https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc324.htm

Fórmula:
EWMA_t = λY_t + (1-λ)EWMA_(t-1)

Uso:
baseline adaptativo para receita, despesa, saldo e fluxo.

### CUSUM
NIST/SEMATECH Engineering Statistics Handbook — CUSUM Control Charts.
https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm

Uso:
detectar pequenos desvios persistentes.

### MAD / robust statistics
NIST — Median Absolute Deviation.
https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/mad.htm

NIST — Detection of Outliers / Modified Z-score.
https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm

Fórmulas:
MAD = median(|x - median(x)|)
M_i = 0.6745(x_i - median(x)) / MAD

Uso:
detecção robusta de extremos financeiros.

### Page / Page-Hinkley
Page, E. S. Continuous Inspection Schemes. Biometrika, 1954.
A família de métodos de mudança cumulativa inspira Page-Hinkley.

Referência de implementação/documentação:
https://github.com/scikit-multiflow/scikit-multiflow/blob/master/src/skmultiflow/drift_detection/page_hinkley.py

Uso:
mudança de regime.

### STL
Cleveland, R. B.; Cleveland, W. S.; McRae, J. E.; Terpenning, I. STL: A Seasonal-Trend Decomposition Procedure Based on Loess. Journal of Official Statistics, 1990.
https://www.math.unm.edu/~lil/Stat581/STL.pdf

Uso:
separar trend + seasonal + remainder quando houver histórico suficiente.

### Isolation Forest
Liu, F. T.; Ting, K. M.; Zhou, Z.-H. Isolation Forest. ICDM 2008.
https://doi.org/10.1109/ICDM.2008.17

Uso:
anomalia multivariada em features agregadas.

## Cash-flow underwriting

FinRegLab — Sharpening the Focus / Cash-flow data for small business underwriting, 2025.
https://finreglab.org/press-releases/finreglab-study-shows-cash-flow-data-can-expand-small-business-lending/

O estudo analisou mais de 38 mil empréstimos de pequenos negócios e reportou valor preditivo adicional de variáveis de cash flow em relação a inputs tradicionais em determinados grupos.

FinRegLab — Empirical Research Findings.
https://finreglab.org/research/the-use-of-cash-flow-data-in-underwriting-credit-empirical-research-findings/

Uso:
base para priorizar sinais derivados de transações e fluxo de caixa.

## Concentração — HHI

U.S. Department of Justice — Herfindahl-Hirschman Index.
https://www.justice.gov/atr/herfindahl-hirschman-index

Fórmula:
HHI = Σ s_i²

Uso no ScorByte:
adaptação matemática para concentração de receita por cliente/pagador.

Importante:
thresholds de antitruste NÃO devem ser reutilizados como thresholds de risco de crédito.

## DSCR

Office of the Comptroller of the Currency — Commercial Real Estate Lending handbook.
https://www.occ.treas.gov/publications-and-resources/publications/comptrollers-handbook/files/commercial-real-estate-lending/pub-ch-commercial-real-estate-previous.pdf

Definição geral:
Debt Service Coverage Ratio = cash flow ou NOI / debt service.

Uso no ScorByte:
criar dscr_proxy com definição explícita do numerador, sem afirmar equivalência regulatória.

## Drift

Population Stability Index — literatura aplicada em credit risk:
https://www.mdpi.com/2227-7390/11/2/492

Fórmula:
PSI = Σ (T_j - B_j) ln(T_j / B_j)

Uso:
monitoramento de mudança de distribuição, como indicador complementar.

## Segurança Open Finance Brasil

Open Finance Brasil — Perfil de Segurança / FAPI.
https://openfinancebrasil.atlassian.net/wiki/spaces/OF/pages/240648789

FAPI-BR v2.2.1, publicada em 07/07/2026:
https://openfinancebrasil.atlassian.net/wiki/spaces/OF/pages/1957625885/FAPI-BR+v2.2.1+-+Open+Finance+Brasil+Financial-grade+API+Security+Profile

Regra:
consultar a versão oficial vigente na data de implementação.

## Observação metodológica

Nem todos os elementos do ScorByte são “algoritmos de paper”.

Categorias:

Métodos estabelecidos:
- Logistic Regression;
- TF-IDF;
- CatBoost;
- EWMA;
- MAD;
- CUSUM;
- Page-Hinkley/change detection;
- STL;
- Isolation Forest;
- SHAP;
- probability calibration.

Índices/fórmulas conhecidas adaptadas:
- HHI para concentração de clientes;
- DSCR proxy;
- CV;
- PSI.

Engenharia própria a validar:
- taxonomy financeira final;
- relationship engine;
- sustainable_revenue_v0;
- financial weighted error;
- combinação final dos sinais.

Nunca mascarar adaptação de engenharia como consenso acadêmico.
