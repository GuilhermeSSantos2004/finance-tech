# ScorByte — Blueprint de Implementação do Motor de Inteligência Financeira

Este diretório transforma as decisões técnicas do projeto em um plano executável para evolução do ScorByte.

O objetivo não é adicionar algoritmos por quantidade. Cada componente deve gerar um sinal financeiro útil, ser testável e permanecer no produto somente se demonstrar ganho mensurável.

## Objetivo do produto

O ScorByte deve evoluir de um classificador BUSINESS/PERSONAL para um motor capaz de transformar dados consentidos do Open Finance em sinais explicáveis sobre:

- natureza da movimentação;
- separação entre vida pessoal e atividade do MEI;
- receita efetivamente identificada;
- estabilidade e volatilidade;
- concentração de receita;
- comportamento anômalo;
- fluxo de caixa;
- compromissos de dívida;
- capacidade financeira.

Importante: o projeto atual NÃO é um modelo de risco de inadimplência. Um futuro modelo de PD/default exige dados históricos de concessão e desempenho do crédito.

## Princípio central

Todo algoritmo candidato segue o fluxo:

1. implementar atrás de configuração/feature flag;
2. testar no benchmark sem contaminar o holdout;
3. comparar contra o baseline;
4. executar ablation test;
5. avaliar precisão, cobertura, calibração e impacto financeiro dos erros;
6. manter somente se houver ganho ou função complementar comprovada.

## Ordem de leitura para uma IA de implementação

1. 01_ARQUITETURA_E_ESTADO_ATUAL.md
2. 02_TRANSACTION_INTELLIGENCE.md
3. 03_BEHAVIORAL_ANOMALY_ENGINE.md
4. 04_FINANCIAL_CAPACITY_ENGINE.md
5. 05_VALIDACAO_BENCHMARK_E_ABLATION.md
6. 06_EXPLICABILIDADE_SEGURANCA_GOVERNANCA.md
7. 07_PLANO_EXECUCAO_PARA_AGENTE.md
8. REFERENCES.md

## Stack alvo

### Transaction Intelligence
- TF-IDF de character n-grams + Logistic Regression — baseline existente.
- CatBoost — challenger.
- probability calibration — Platt/isotonic quando os dados permitirem.
- selective classification / REVIEW.
- ensemble apenas se superar os modelos individuais no holdout.

### Financial Semantics
Segundo nível de classificação:
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

### Behavioral Intelligence
- EWMA/EMA;
- bandas estatísticas;
- Median + MAD / modified z-score;
- CUSUM;
- Page-Hinkley/change detection;
- STL para sazonalidade quando houver histórico suficiente;
- Isolation Forest como detector multivariado posterior.

### Financial Capacity
- receita verificada;
- renda/receita sustentável estimada;
- Free Cash Flow;
- DSCR;
- HHI adaptado para concentração de pagadores/clientes;
- coeficiente de variação;
- tendência 30/90/180/365 dias;
- recorrência;
- concentração;
- dependência de contrapartes.

### Explainability e monitoramento
- SHAP quando houver CatBoost;
- model card e versionamento;
- audit trail;
- probability calibration;
- PSI e testes de distribuição/drift;
- métricas por banco, CNAE e perfil.

## Regra sobre fontes e matemática

Os documentos distinguem três categorias:

1. método acadêmico/estatístico estabelecido;
2. adaptação de método conhecido para o domínio financeiro;
3. métrica de engenharia própria do ScorByte.

Nunca apresentar uma métrica própria como padrão acadêmico ou regulatório.

## Segurança

A segurança não é resolvida pelo modelo. O motor deve minimizar PII e manter auditabilidade, mas a integração Open Finance real deve seguir a especificação de segurança vigente do ecossistema, consentimento, autenticação/autorização, criptografia, gestão de segredos e políticas de retenção.

## Dataset

- data/training: somente treino.
- data/benchmark: holdout/benchmark; NÃO mover para treinamento.
- correções humanas futuras devem registrar fonte do rótulo e confiança.
- splits devem ser por conta/usuário e também temporais quando houver histórico real.
