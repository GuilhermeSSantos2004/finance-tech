# Contrato dos dados

Este documento define os campos esperados para treinamento e inferência. O objetivo é impedir que o modelo seja treinado com informações que não estarão disponíveis em produção.

## Formatos aceitos

O carregador aceita quatro formatos.

### Dataset com metadados

```json
{
  "datasetMetadata": {
    "recordCount": 1
  },
  "transactions": []
}
```

### Lista direta

```json
[
  {}
]
```

### Envelope de uma transação

```json
{
  "transaction": {}
}
```

### Transação direta

```json
{
  "descriptionRaw": "RSCSS MATCONST 0109"
}
```

## Campos mínimos

| Campo | Treinamento | Inferência | Observação |
|---|:---:|:---:|---|
| `descriptionRaw` ou `description` | Sim | Sim | Pelo menos um precisa existir |
| `amount` | Sim | Sim | Número positivo ou negativo |
| `type` | Sim | Sim | `CREDIT` ou `DEBIT` |
| `accountId` | Sim | Não | Usado para divisão por grupo, nunca como feature |
| `target.classification` | Sim | Não | Resposta correta usada somente no treino |

## Campos recomendados

- `date` e `timezone`;
- `currencyCode`;
- `category` e `categoryId`, se realmente vierem do banco;
- `operationType`;
- `providerCode`;
- `paymentData.paymentMethod`;
- pagador e recebedor;
- estabelecimento;
- `businessContext.mainCnae`;
- `businessContext.businessActivity`;
- atributos históricos calculados somente com eventos anteriores.

## Exemplo para treinamento

```json
{
  "id": "transaction-id",
  "description": "COMPRA MAT CONST",
  "descriptionRaw": "RSCSS MATCONST 0109 T04",
  "currencyCode": "BRL",
  "amount": -760.4,
  "date": "2026-09-01T14:20:00.000Z",
  "timezone": "America/Sao_Paulo",
  "category": "Shopping",
  "accountId": "account-group-id",
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
    "name": "MATERIAIS TESTE LTDA",
    "documentNumber": {
      "type": "CNPJ",
      "value": "CNPJ_NAO_ENVIADO_AO_MODELO"
    }
  },
  "businessContext": {
    "companyType": "MEI",
    "mainCnae": "4330-4/04",
    "businessActivity": "Servicos de pintura de edificios em geral"
  },
  "derivedFeatures": {
    "counterpartyTransactions30d": 2,
    "counterpartyTransactions90d": 5,
    "amountRatioToMedian90d": 1.08,
    "sameAmountOccurrences90d": 0,
    "recurrenceType": "IRREGULAR"
  },
  "target": {
    "classification": "BUSINESS",
    "labelSource": "HUMAN_REVIEW",
    "labelConfidence": 1.0
  }
}
```

## Campo `target`

Durante o treinamento:

```json
{
  "target": {
    "classification": "BUSINESS",
    "labelSource": "HUMAN_REVIEW",
    "labelConfidence": 1.0
  }
}
```

Valores aceitos em `classification`:

- `BUSINESS`;
- `PERSONAL`.

`REVIEW` é uma decisão de inferência. Uma transação incerta só deve entrar no treinamento depois de ser revisada e receber um rótulo confirmado.

O objeto `target` nunca pode ser incluído nas variáveis do modelo.

## Identificação da contraparte

A aplicação deve selecionar a contraparte conforme a direção:

- crédito: normalmente o `payer` é a contraparte;
- débito: normalmente o `receiver` ou `merchant` é a contraparte.

O pagador de um débito costuma ser o próprio titular da conta. O fato de ele possuir CNPJ não torna automaticamente a despesa comercial.

## Horário

Datas terminadas em `Z` estão em UTC. O algoritmo converte a data usando `timezone`, por exemplo `America/Sao_Paulo`, antes de calcular hora e dia da semana.

Quando `derivedFeatures.localHour` e `localWeekday` já existem, eles possuem prioridade.

## Recorrência sem vazamento temporal

Para classificar uma transação ocorrida no instante `T`, os atributos históricos só podem usar transações anteriores a `T`.

Exemplos corretos:

- quantidade para a contraparte nos 30 dias anteriores;
- mediana dos valores nos 90 dias anteriores;
- repetição de valores antes da transação atual.

Utilizar movimentações futuras faria o teste enxergar informações indisponíveis no momento real da decisão.

## Campos excluídos

Os seguintes campos não entram como variáveis preditivas:

- `target`;
- `id`;
- `accountId`;
- CPF ou CNPJ completo;
- `referenceNumber`;
- código de barras;
- `receiverReferenceId`;
- `createdAt` e `updatedAt`;
- `order`.

`accountId` continua sendo necessário durante o treinamento para separar contas sem vazamento.

## Categoria bancária

`category` e `categoryId` só devem ser usados se forem fornecidos pelo mesmo processo em produção.

Se a categoria tiver sido criada manualmente ou por uma IA que já conhecia a resposta final, ela provoca vazamento e precisa ser removida.

## Saída da inferência

```json
{
  "classification": "REVIEW",
  "modelClass": "BUSINESS",
  "probabilities": {
    "BUSINESS": 0.67,
    "PERSONAL": 0.33
  },
  "confidence": 0.67,
  "requiresReview": true,
  "modelVersion": "0.1.0"
}
```

Diferença entre os campos:

- `modelClass`: classe binária mais provável;
- `classification`: decisão final após aplicar os limites;
- `requiresReview`: indica que uma pessoa precisa confirmar o resultado.

## Privacidade

- Não usar CPF real nos datasets de desenvolvimento.
- Não enviar CPF/CNPJ completo ao modelo.
- Usar tokens ou hashes estáveis quando a recorrência da contraparte for necessária.
- Controlar acesso aos datasets reais.
- Registrar a origem e a autorização dos rótulos.
- Não publicar transações reais em repositórios públicos.

