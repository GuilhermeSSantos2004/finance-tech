# Dados de treinamento

Esta pasta e a fonte padrao de dados supervisionados do classificador.

## Como funciona

O comando:

```bash
python -m finance_classifier train
```

procura automaticamente todos os arquivos `.json` diretamente dentro de `data/training/` e combina as transacoes em um unico conjunto de treinamento.

Para adicionar dados novos:

1. crie ou copie um arquivo `.json` valido para esta pasta;
2. cada registro de treino precisa conter `target.classification` com `BUSINESS` ou `PERSONAL`;
3. cada registro precisa ter `accountId`, usado para separar contas entre treino e teste;
4. execute novamente `python -m finance_classifier train`.

Nao e necessario editar o codigo nem informar os nomes dos arquivos.

## Importante

Nao mova arquivos de `data/benchmark/` para esta pasta. O benchmark deve continuar fora do treinamento para medir generalizacao em dados que o modelo nao viu.
