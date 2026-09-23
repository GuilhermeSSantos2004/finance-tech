# Finance Tech — Blind Benchmark 140

Benchmark sintético para testar o classificador `BUSINESS` vs `PERSONAL` do repositório `GuilhermeSSantos2004/finance-tech` sem entregar o rótulo ao modelo.

## Conteúdo

- `benchmark_140_blind.json`: **entrada do modelo**. Tem 140 transações, sem `target`, dificuldade, motivo ou rótulo esperado.
- `benchmark_140_gold.json`: **gabarito**. Tem a classe correta, nível de dificuldade, cenário e racional humano. Não deve ser usado no treino nem na inferência.
- `benchmark_140_openfinance_v2_5_reference.json`: representação de referência dos mesmos 140 registros com os principais campos de transação da API Accounts v2.5 do Open Finance Brasil.
- `score_benchmark.py`: compara a saída do seu CLI com o gabarito.

## Distribuição

O conjunto é balanceado: 70 `BUSINESS` + 70 `PERSONAL`.

Por classe:

| Nível | Registros por classe | Total | Objetivo |
|---|---:|---:|---|
| EASY | 15 | 30 | Sinais coerentes em texto, contraparte, categoria e contexto |
| MEDIUM | 20 | 40 | Um ou mais sinais ambíguos; exige combinar contexto e histórico |
| HARD | 20 | 40 | Transações plausíveis nas duas classes, descrições truncadas e categorias pouco úteis |
| ADVERSARIAL | 15 | 30 | Sinais superficiais contradizem o gabarito: pequeno valor comercial, alto crédito pessoal, CPF comercial, CNPJ pessoal, horário atípico ou categoria enganosa |

## Por que esse benchmark é mais difícil que os 60 dados atuais

O conjunto original tem 30 transações comerciais e 30 pessoais. O benchmark não reutiliza os IDs de conta nem as contrapartes originais. Ele mantém os seis CNAEs já conhecidos pelo modelo para medir generalização sem introduzir, ao mesmo tempo, o problema adicional de CNAEs totalmente desconhecidos.

Os casos foram desenhados para quebrar heurísticas simples como:

- `CREDIT` = comercial;
- valor alto = comercial;
- CNPJ = comercial;
- CPF = pessoal;
- horário comercial = comercial;
- categoria `Shopping` = pessoal;
- estabelecimento relacionado ao CNAE = comercial.

## Uso correto

Não treine com `benchmark_140_blind.json`. Use-o como holdout.

Primeiro treine o modelo normalmente:

```powershell
python -m finance_classifier train --business data/synthetic/transacoes_comerciais_30.json --personal data/synthetic/transacoes_pessoais_30.json --output artifacts
```

Depois rode a inferência:

```powershell
python -m finance_classifier predict --model artifacts/transaction_classifier.joblib --input data/benchmark/benchmark_140_blind.json --output artifacts/benchmark_predictions.json
```

Por fim calcule o resultado:

```powershell
python data/benchmark/score_benchmark.py --predictions artifacts/benchmark_predictions.json --gold data/benchmark/benchmark_140_gold.json --output artifacts/benchmark_score.json
```

## Métricas do scorer

- `strictAccuracy`: acerto final sobre todos os 140. `REVIEW` não conta como acerto.
- `coverage`: percentual em que o sistema tomou decisão automática (`BUSINESS` ou `PERSONAL`).
- `reviewRate`: percentual enviado para revisão humana.
- `autoDecisionAccuracy`: precisão apenas nas decisões automáticas. É a métrica mais importante quando `REVIEW` é uma abstenção legítima.
- `autoDecisionErrors`: decisões automáticas erradas. Deve ser acompanhado separadamente de `REVIEW`.
- `binaryModelClassAccuracy`: compara `modelClass` com o gabarito mesmo quando a decisão final é `REVIEW`. Isso mostra se a direção binária do modelo estava correta, ainda que sem confiança suficiente.
- `byDifficulty`: separa o resultado em EASY, MEDIUM, HARD e ADVERSARIAL.
- `byExpectedClass`: separa BUSINESS de PERSONAL para detectar assimetria.

## Interpretação recomendada

Não use a acurácia total deste conjunto sintético como evidência de produção. Ele serve para desenvolvimento, regressão e comparação entre versões.

Para o produto, acompanhe principalmente:

1. erros automáticos `PERSONAL -> BUSINESS`, porque uma despesa pessoal marcada como empresarial é um erro potencialmente mais grave;
2. erros automáticos `BUSINESS -> PERSONAL`;
3. taxa de `REVIEW`;
4. desempenho por dificuldade, CNAE e banco;
5. calibração das probabilidades em dados reais revisados por humanos.

## Alinhamento com Open Finance Brasil

O contrato do projeto `finance-tech` não é uma cópia 1:1 da API oficial. Ele usa campos internos como `descriptionRaw`, `amount`, `type`, `operationType`, `paymentData` e `businessContext`.

O benchmark preserva esse contrato para funcionar no seu código atual, mas usa valores compatíveis com a semântica da API Accounts v2.5:

| Finance Tech | Open Finance Brasil Accounts v2.5 |
|---|---|
| `id` | `transactionId` |
| `descriptionRaw` | `transactionName` |
| `type=CREDIT/DEBIT` | `creditDebitType=CREDITO/DEBITO` |
| `operationType` | `type` |
| `abs(amount)` + `currencyCode` | `transactionAmount.amount` + `currency` |
| `date` | `transactionDateTime` |
| contraparte em `paymentData` / `counterpartyData` | `partieCnpjCpf` + `partiePersonType` |

Os tipos usados em `operationType` foram limitados ao enum oficial relevante (`PIX`, `BOLETO`, `CARTAO`, `CONVENIO_ARRECADACAO`, `SAQUE`, etc.).

## Fontes de referência

- Open Finance Brasil — API Accounts / transações: https://github.com/OpenBanking-Brasil/all-services-repo/blob/main/api_accounts_-_open_finance_brasil/2.5.0.yaml
- Área do Desenvolvedor — orientações da API de Contas: https://openfinancebrasil.atlassian.net/wiki/spaces/OF/pages/1739096252/Orienta%2Bes%2B-%2BDC%2BContas

## Observação de privacidade

Todos os dados são sintéticos. Os documentos presentes foram gerados apenas para respeitar o formato esperado e não devem ser interpretados como movimentações reais ou identidade de pessoas/empresas reais.