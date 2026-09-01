# Finance Tech — classificador de transações para MEI

Base inicial em Python para classificar transações bancárias como:

- `BUSINESS`: ligada à operação do MEI;
- `PERSONAL`: ligada à vida pessoal do titular;
- `REVIEW`: resultado incerto que precisa de confirmação humana.

O projeto combina descrições bancárias incompletas com o contexto da empresa. A primeira versão usa **TF-IDF de caracteres**, atributos estruturados e **Regressão Logística**. Essa escolha é mais segura que começar diretamente com LightGBM enquanto o volume real ainda é pequeno: os n-grams de caracteres reconhecem abreviações como `RSCSS`, `PIXREC`, nomes cortados e códigos misturados.

## Estado atual

- 60 transações sintéticas balanceadas: 30 comerciais e 30 pessoais;
- 6 contas e 6 CNAEs;
- créditos e débitos igualmente distribuídos entre as classes;
- divisão de treino e teste por `accountId`, evitando que a mesma conta apareça nos dois lados;
- exclusão de CPF/CNPJ completo, IDs e rótulos das variáveis do modelo;
- zona de incerteza: abaixo de `20%` comercial resulta em `PERSONAL`, acima de `80%` resulta em `BUSINESS` e o intervalo intermediário resulta em `REVIEW`;
- testes automatizados e CI no GitHub Actions.

> Os CNPJs do dataset são sintéticos e possuem dígitos verificadores válidos. Eles não representam movimentações financeiras de empresas reais. Os dados são adequados para validar o pipeline, não para colocar o modelo em produção.

## Estrutura

```text
data/synthetic/             datasets separados por classe
src/finance_classifier/     carregamento, features, modelo, treino e CLI
tests/                      testes de dados, vazamento e modelo
artifacts/                  saída local dos treinamentos, ignorada pelo Git
.github/workflows/ci.yml    validação automática
```

## Preparação

Requer Python 3.11 ou superior.

```bash
python -m venv .venv
```

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

No Linux ou macOS:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## Treinamento

```bash
python -m finance_classifier train \
  --business data/synthetic/transacoes_comerciais_30.json \
  --personal data/synthetic/transacoes_pessoais_30.json \
  --output artifacts
```

O comando gera localmente:

- `artifacts/transaction_classifier.joblib`;
- `artifacts/metrics.json`;
- `artifacts/model_card.json`.

Os artefatos não são versionados porque podem ser reproduzidos a partir dos dados e do código.

## Inferência

O arquivo de entrada pode conter uma transação, uma lista ou um objeto com a chave `transactions`.

```bash
python -m finance_classifier predict \
  --model artifacts/transaction_classifier.joblib \
  --input data/synthetic/transacoes_comerciais_30.json
```

Exemplo de saída:

```json
{
  "predictions": [
    {
      "id": "identificador-da-transacao",
      "classification": "BUSINESS",
      "modelClass": "BUSINESS",
      "probabilities": {
        "BUSINESS": 0.91,
        "PERSONAL": 0.09
      },
      "confidence": 0.91,
      "requiresReview": false,
      "modelVersion": "0.1.0"
    }
  ]
}
```

## Testes

```bash
python -m unittest discover -s tests -v
```

Os testes verificam:

- balanceamento e leitura dos datasets;
- ausência de contas repetidas entre treino e teste;
- exclusão de identificadores e do `target` nas features;
- treino, inferência e persistência do modelo;
- geração das métricas e do model card.

## Próximas etapas

1. Coletar transações reais revisadas por pessoas e por diferentes CNAEs, bancos e períodos.
2. Registrar correções do usuário como novos rótulos, com fonte e confiança.
3. Comparar o baseline com LightGBM ou CatBoost quando houver volume suficiente.
4. Calibrar probabilidades e limites de `REVIEW` usando dados reais de validação.
5. Expor o classificador por uma API FastAPI depois de estabilizar o contrato de entrada.
6. Monitorar mudança de distribuição, erros por CNAE e taxa de revisão manual.

