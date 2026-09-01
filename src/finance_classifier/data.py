"""Dataset loading and validation utilities."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping


SUPPORTED_LABELS = frozenset({"BUSINESS", "PERSONAL"})


class DatasetValidationError(ValueError):
    """Raised when a transaction dataset does not match the expected contract."""


def _read_json(path: str | Path) -> Any:
    source = Path(path)
    try:
        return json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DatasetValidationError(f"Arquivo nao encontrado: {source}") from exc
    except json.JSONDecodeError as exc:
        raise DatasetValidationError(
            f"JSON invalido em {source}, linha {exc.lineno}, coluna {exc.colno}"
        ) from exc


def extract_transactions(payload: Any, *, source: str = "<memory>") -> list[dict[str, Any]]:
    """Extract a transaction list from either a raw array or a dataset envelope."""
    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, Mapping) and isinstance(payload.get("transactions"), list):
        records = payload["transactions"]
    elif isinstance(payload, Mapping) and isinstance(payload.get("transaction"), Mapping):
        records = [payload["transaction"]]
    elif isinstance(payload, Mapping):
        records = [payload]
    else:
        raise DatasetValidationError(
            f"{source}: esperado objeto, lista ou objeto com a chave 'transactions'"
        )

    normalized: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            raise DatasetValidationError(f"{source}: registro {index} nao e um objeto JSON")
        normalized.append(dict(record))
    return normalized


def validate_transaction(
    transaction: Mapping[str, Any],
    *,
    source: str,
    index: int,
    require_target: bool,
) -> None:
    prefix = f"{source}: registro {index}"
    if not transaction.get("descriptionRaw") and not transaction.get("description"):
        raise DatasetValidationError(f"{prefix}: descricao ausente")

    amount = transaction.get("amount")
    if not isinstance(amount, (int, float)) or isinstance(amount, bool):
        raise DatasetValidationError(f"{prefix}: amount deve ser numerico")

    tx_type = str(transaction.get("type", "")).upper()
    if tx_type not in {"CREDIT", "DEBIT"}:
        raise DatasetValidationError(f"{prefix}: type deve ser CREDIT ou DEBIT")

    if require_target:
        target = transaction.get("target")
        if not isinstance(target, Mapping):
            raise DatasetValidationError(f"{prefix}: target ausente")
        label = str(target.get("classification", "")).upper()
        if label not in SUPPORTED_LABELS:
            raise DatasetValidationError(
                f"{prefix}: target.classification deve ser BUSINESS ou PERSONAL"
            )
        if not transaction.get("accountId"):
            raise DatasetValidationError(f"{prefix}: accountId ausente para divisao por grupo")


def load_transactions(
    paths: Iterable[str | Path], *, require_target: bool
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in paths:
        source = str(Path(path))
        for index, transaction in enumerate(extract_transactions(_read_json(path), source=source)):
            validate_transaction(
                transaction,
                source=source,
                index=index,
                require_target=require_target,
            )
            records.append(transaction)
    if not records:
        raise DatasetValidationError("Nenhuma transacao encontrada")
    return records


def load_training_data(
    paths: Iterable[str | Path],
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    """Return transactions, labels and account groups for supervised training."""
    records = load_transactions(paths, require_target=True)
    labels = [str(record["target"]["classification"]).upper() for record in records]
    groups = [str(record["accountId"]) for record in records]

    missing = SUPPORTED_LABELS.difference(labels)
    if missing:
        raise DatasetValidationError(
            "Dataset precisa conter as duas classes; ausente: " + ", ".join(sorted(missing))
        )
    if len(set(groups)) < 2:
        raise DatasetValidationError(
            "Dataset precisa conter pelo menos duas contas para avaliacao sem vazamento"
        )
    return records, labels, groups


def dataset_summary(records: list[dict[str, Any]], labels: list[str]) -> dict[str, Any]:
    cnaes = {
        str(record.get("businessContext", {}).get("mainCnae", "UNKNOWN"))
        for record in records
    }
    return {
        "records": len(records),
        "labels": dict(sorted(Counter(labels).items())),
        "accounts": len({str(record.get("accountId")) for record in records}),
        "cnaes": sorted(cnaes),
    }

