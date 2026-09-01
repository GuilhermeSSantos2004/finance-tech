"""Group-aware training, evaluation and artifact generation."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import GroupShuffleSplit

from finance_classifier.data import dataset_summary
from finance_classifier.model import LABEL_BUSINESS, LABEL_PERSONAL, TransactionClassifier


def group_split_indices(
    labels: Sequence[str],
    groups: Sequence[str],
    *,
    test_size: float = 0.25,
    random_state: int = 42,
) -> tuple[list[int], list[int]]:
    if len(labels) != len(groups):
        raise ValueError("labels e groups devem ter o mesmo tamanho")
    if len(set(groups)) < 2:
        raise ValueError("Sao necessarios pelo menos dois grupos")

    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=test_size,
        random_state=random_state,
    )
    train_indices, test_indices = next(splitter.split(labels, labels, groups=groups))
    train = [int(index) for index in train_indices]
    test = [int(index) for index in test_indices]

    train_labels = {labels[index] for index in train}
    test_labels = {labels[index] for index in test}
    expected = {LABEL_BUSINESS, LABEL_PERSONAL}
    if train_labels != expected or test_labels != expected:
        raise ValueError(
            "A divisao por conta nao preservou as duas classes; adicione mais contas rotuladas"
        )
    return train, test


def _subset(items: Sequence[Any], indices: Sequence[int]) -> list[Any]:
    return [items[index] for index in indices]


def evaluate_holdout(
    transactions: Sequence[Mapping[str, Any]],
    labels: Sequence[str],
    groups: Sequence[str],
    *,
    test_size: float = 0.25,
    random_state: int = 42,
) -> dict[str, Any]:
    train_indices, test_indices = group_split_indices(
        labels,
        groups,
        test_size=test_size,
        random_state=random_state,
    )
    train_transactions = _subset(transactions, train_indices)
    train_labels = _subset(labels, train_indices)
    test_transactions = _subset(transactions, test_indices)
    test_labels = _subset(labels, test_indices)

    classifier = TransactionClassifier(random_state=random_state)
    classifier.fit(train_transactions, train_labels)
    predicted = [classifier.predict_one(transaction).model_class for transaction in test_transactions]
    probability_business = classifier.predict_business_probability(test_transactions)
    binary_truth = [1 if label == LABEL_BUSINESS else 0 for label in test_labels]

    report = classification_report(
        test_labels,
        predicted,
        labels=[LABEL_BUSINESS, LABEL_PERSONAL],
        output_dict=True,
        zero_division=0,
    )
    matrix = confusion_matrix(
        test_labels,
        predicted,
        labels=[LABEL_BUSINESS, LABEL_PERSONAL],
    )
    return {
        "split": {
            "strategy": "GroupShuffleSplit(accountId)",
            "randomState": random_state,
            "testSize": test_size,
            "trainRecords": len(train_indices),
            "testRecords": len(test_indices),
            "trainGroups": len({groups[index] for index in train_indices}),
            "testGroups": len({groups[index] for index in test_indices}),
            "groupOverlap": sorted(
                {groups[index] for index in train_indices}.intersection(
                    {groups[index] for index in test_indices}
                )
            ),
        },
        "metrics": {
            "accuracy": float(accuracy_score(test_labels, predicted)),
            "balancedAccuracy": float(balanced_accuracy_score(test_labels, predicted)),
            "rocAucBusiness": float(roc_auc_score(binary_truth, probability_business)),
            "classificationReport": report,
            "confusionMatrix": {
                "labels": [LABEL_BUSINESS, LABEL_PERSONAL],
                "values": matrix.tolist(),
            },
        },
    }


def train_and_save(
    transactions: Sequence[Mapping[str, Any]],
    labels: Sequence[str],
    groups: Sequence[str],
    *,
    output_dir: str | Path,
    test_size: float = 0.25,
    random_state: int = 42,
) -> dict[str, Any]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    evaluation = evaluate_holdout(
        transactions,
        labels,
        groups,
        test_size=test_size,
        random_state=random_state,
    )
    final_classifier = TransactionClassifier(random_state=random_state)
    final_classifier.fit(transactions, labels)
    model_path = final_classifier.save(destination / "transaction_classifier.joblib")

    summary = dataset_summary(list(transactions), list(labels))
    generated_at = datetime.now(timezone.utc).isoformat()
    metrics_payload = {
        "generatedAt": generated_at,
        "dataset": summary,
        **evaluation,
    }
    model_card = {
        "modelName": "finance-transaction-classifier",
        "modelVersion": "0.1.0",
        "generatedAt": generated_at,
        "algorithm": "TF-IDF de caracteres + atributos estruturados + Regressao Logistica",
        "trainingRecords": len(transactions),
        "classDistribution": dict(sorted(Counter(labels).items())),
        "decisionThresholds": {"PERSONAL_MAX": 0.20, "BUSINESS_MIN": 0.80},
        "limitations": [
            "Dados atuais sao sinteticos e insuficientes para producao.",
            "Previsoes na zona intermediaria devem ser revisadas por uma pessoa.",
            "A classificacao nao substitui orientacao contabil ou fiscal.",
        ],
        "excludedLeakageFields": [
            "target",
            "id",
            "accountId como atributo preditivo",
            "CPF/CNPJ completo",
            "referenceNumber",
        ],
    }

    metrics_path = destination / "metrics.json"
    card_path = destination / "model_card.json"
    metrics_path.write_text(
        json.dumps(metrics_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    card_path.write_text(
        json.dumps(model_card, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "model": str(model_path),
        "metrics": str(metrics_path),
        "modelCard": str(card_path),
        "evaluation": evaluation,
    }

