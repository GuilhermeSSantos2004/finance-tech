# 06 — Explicabilidade, segurança e governança

## 1. Explicabilidade

### Logistic Regression

Expor:
- coeficientes;
- top features positivas/negativas;
- grupos de features.

### CatBoost + SHAP

SHAP atribui contribuição de features para uma previsão.

Forma aditiva:

f(x) ≈ φ0 + Σ φ_i

onde φ_i representa a contribuição da feature i.

Saída de produto sugerida:

Fatores positivos:
- receita recorrente;
- múltiplos pagadores;
- fluxo positivo.

Fatores de atenção:
- concentração;
- queda recente;
- crescimento de despesas.

### Regra

Explicação é sobre o modelo/indicadores observados. Não transformar SHAP em causalidade.

“Feature contribuiu para a previsão” ≠ “feature causou o risco”.

## 2. Audit trail

Registrar por análise:
- request/análise ID;
- usuário/tenant;
- consent context ID quando aplicável;
- fontes de dados;
- período analisado;
- modelVersion;
- featureVersion;
- parâmetros;
- classificação;
- probabilidade calibrada;
- REVIEW;
- indicadores financeiros;
- explicações;
- timestamp.

Evitar armazenar PII desnecessária no log.

## 3. Segurança do modelo

Já preservar:
- CPF/CNPJ completo fora das features;
- accountId fora das features;
- target fora da inferência;
- benchmark fora do treino.

Adicionar:
- validação de schema;
- proteção contra campos inesperados;
- limites de tamanho;
- versionamento;
- trilha de origem do rótulo;
- testes contra leakage.

## 4. Segurança de produto

Algoritmos NÃO resolvem segurança de Open Finance.

Integração real deve considerar a especificação vigente do Open Finance Brasil.

Itens:
- consentimento;
- OAuth 2.0 / OpenID Connect conforme perfil aplicável;
- FAPI-BR vigente;
- autenticação e autorização;
- criptografia em trânsito;
- proteção de dados em repouso;
- gestão de segredos/chaves;
- RBAC/ABAC;
- isolamento entre clientes/tenants;
- auditoria;
- retenção e exclusão;
- mínimo privilégio;
- rotação de credenciais.

Não copiar parâmetros de segurança antigos para produção. Consultar sempre a especificação oficial vigente.

## 5. Minimização

Coletar/processar somente o necessário para o caso de uso.

Separar:
- identificadores operacionais;
- dados brutos;
- features derivadas;
- outputs de modelo.

Sempre que possível, o pipeline de modelagem trabalha com features derivadas e identificadores pseudônimos.

## 6. Dados sensíveis / proxies

Auditar features que possam funcionar como proxies inadequados.

Não usar atributos protegidos/sensíveis para inferir capacidade de crédito sem base jurídica, técnica e de governança adequada.

Avaliar fairness quando houver dados e contexto legal apropriados.

## 7. Governança do modelo

Cada versão deve possuir model card:
- objetivo;
- população alvo;
- dados;
- features;
- algoritmo;
- métricas;
- limitações;
- subgrupos;
- calibração;
- thresholds;
- data de treino;
- responsável;
- versão.

## 8. Human-in-the-loop

REVIEW deve registrar:
- classificação do modelo;
- confiança;
- motivo da revisão;
- decisão humana;
- labelSource;
- labelConfidence.

Correção humana não deve entrar automaticamente no treino sem controle de qualidade.

## 9. Segurança + feedback do professor

O feedback recebido pede:
- segurança mais bem trabalhada;
- estratégia de uso pelo MEI mais clara.

Resposta técnica esperada:

MEI solicita crédito na instituição
→ autoriza compartilhamento via Open Finance
→ instituição envia/permite dados ao fluxo autorizado
→ ScorByte processa
→ retorna indicadores explicáveis
→ instituição usa os sinais dentro de sua política.

O ScorByte deve ser apresentado como infraestrutura B2B integrada à jornada de crédito, não necessariamente como um aplicativo que exige uso diário do MEI.

## 10. Limite de decisão

Enquanto não houver modelo validado de outcome:
- não rotular “aprovado/reprovado” pelo ML;
- não chamar capacity score de probability of default;
- não afirmar redução de inadimplência sem experimento/dados.
