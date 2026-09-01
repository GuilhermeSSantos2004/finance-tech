# Guia de testes

Este documento mostra como verificar o projeto localmente e explica o que cada teste comprova.

## 1. Preparação

Requer Python 3.11 ou superior.

### Windows PowerShell

```powershell
git clone https://github.com/GuilhermeSSantos2004/finance-tech.git
cd finance-tech
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

### Linux ou macOS

```bash
git clone https://github.com/GuilhermeSSantos2004/finance-tech.git
cd finance-tech
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## 2. Executar testes automatizados

```bash
python -m unittest discover -s tests -v
```

Resultado esperado:

```text
Ran 6 tests

OK
```

### O que é verificado

| Teste | O que comprova |
|---|---|
| Leitura do dataset | Existem 60 registros, 30 por classe e 6 contas |
| Divisão por grupo | Uma conta não aparece simultaneamente no treino e no teste |
| Texto sem vazamento | CNPJ e `target` não entram no ramo textual |
| Dados sem identificadores | IDs e `accountId` não entram como variáveis |
| Persistência | O modelo salvo e carregado mantém a mesma previsão |
| Treinamento | Modelo, métricas e model card são gerados corretamente |

## 3. Executar um treinamento completo

No PowerShell, use uma única linha:

```powershell
python -m finance_classifier train --business data/synthetic/transacoes_comerciais_30.json --personal data/synthetic/transacoes_pessoais_30.json --output artifacts
```

No Linux ou macOS:

```bash
python -m finance_classifier train \
  --business data/synthetic/transacoes_comerciais_30.json \
  --personal data/synthetic/transacoes_pessoais_30.json \
  --output artifacts
```

Arquivos esperados:

```text
artifacts/transaction_classifier.joblib
artifacts/metrics.json
artifacts/model_card.json
```

## 4. Conferir as métricas

Abra `artifacts/metrics.json`. Os pontos principais são:

- `split.groupOverlap` precisa ser uma lista vazia;
- `split.trainGroups` e `split.testGroups` precisam ser maiores que zero;
- `metrics.confusionMatrix` mostra acertos e erros por classe;
- `metrics.balancedAccuracy` evita uma visão enganosa quando as classes ficarem desbalanceadas;
- `metrics.rocAucBusiness` mede a ordenação das probabilidades comerciais.

Resultado atual com a semente `42`:

| Item | Resultado |
|---|---:|
| Registros de treino | 40 |
| Registros de teste | 20 |
| Contas de treino | 4 |
| Contas de teste | 2 |
| Sobreposição | 0 |
| Acurácia balanceada | 0,80 |
| ROC-AUC comercial | 0,92 |

## 5. Testar inferência

Depois do treinamento, classifique o dataset pessoal:

```powershell
python -m finance_classifier predict --model artifacts/transaction_classifier.joblib --input data/synthetic/transacoes_pessoais_30.json --output artifacts/previsoes_pessoais.json
```

O resultado será salvo em `artifacts/previsoes_pessoais.json`.

Na validação atual, os 30 registros pessoais produziram:

- 28 respostas `PERSONAL`;
- 2 respostas `REVIEW`;
- 0 respostas `BUSINESS`.

Esse teste demonstra que o comando de inferência funciona. Ele não representa uma medição de produção porque o modelo já foi treinado com a versão completa desses dados depois da avaliação holdout.

## 6. Testar uma transação inédita

Crie `nova_transacao.json` sem o campo `target`:

```json
{
  "description": "COMPRA MAT CONST",
  "descriptionRaw": "RSCSS MATCONST 0109 T04",
  "currencyCode": "BRL",
  "amount": -760.4,
  "date": "2026-09-01T14:20:00.000Z",
  "timezone": "America/Sao_Paulo",
  "category": "Shopping",
  "providerCode": "BANK_PROVIDER",
  "status": "POSTED",
  "paymentData": {
    "paymentMethod": "DEBIT_CARD",
    "payer": null,
    "receiver": null
  },
  "type": "DEBIT",
  "operationType": "CARTAO",
  "merchant": {
    "name": "MATERIAIS TESTE LTDA"
  },
  "businessContext": {
    "companyType": "MEI",
    "mainCnae": "4330-4/04",
    "businessActivity": "Servicos de pintura de edificios em geral"
  }
}
```

Execute:

```powershell
python -m finance_classifier predict --model artifacts/transaction_classifier.joblib --input nova_transacao.json
```

O resultado pode ser `BUSINESS`, `PERSONAL` ou `REVIEW`. Para transações inéditas, `REVIEW` não significa erro: significa que a probabilidade não atingiu os limites de segurança.

## 7. GitHub Actions

O arquivo `.github/workflows/ci.yml` repete automaticamente três etapas em Python 3.11 e 3.12:

1. instalação do pacote;
2. execução dos testes unitários;
3. treinamento completo como smoke test.

Qualquer alteração enviada ao `main` ou a um pull request será validada novamente.

## 8. Como avaliar com dados reais

Para uma avaliação válida:

1. usar transações reais autorizadas e anonimizadas;
2. rotular por revisão humana;
3. manter contas inteiras fora do treinamento;
4. não alterar o conjunto de teste durante o desenvolvimento;
5. registrar precisão, recall e F1 por classe;
6. analisar separadamente os casos `REVIEW`;
7. comparar desempenho por CNAE e banco.

O objetivo inicial deve ser alta precisão em `BUSINESS`, evitando que uma despesa pessoal seja marcada automaticamente como empresarial.

